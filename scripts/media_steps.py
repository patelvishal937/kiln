"""Deterministic media steps: screenshots → Remotion renders → HeyGen avatar → upload."""

from __future__ import annotations

import asyncio
import json
import mimetypes
import shutil
from pathlib import Path

import httpx

from config import REMOTION_DIR, Settings
from schemas import Blueprint, MediaResult
from state import RunState

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}


# ----------------------------------------------------------------- screenshots
async def capture_screenshots(urls: dict[str, str], out_dir: Path, routes: dict[str, list[str]]) -> list[str]:
    """urls: {"app": base, "site": base}; routes: {"app": ["/", "/dashboard"], ...}. Returns file paths."""
    from playwright.async_api import async_playwright

    shots: list[str] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            for screen, base in urls.items():
                if not base:
                    continue
                for vp_name, (w, h) in VIEWPORTS.items():
                    page = await browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
                    for i, route in enumerate(dict.fromkeys(routes.get(screen) or ["/"])):
                        url = base.rstrip("/") + (route if route.startswith("/") else f"/{route}")
                        try:
                            await page.goto(url, wait_until="networkidle", timeout=45000)
                            await page.wait_for_timeout(1200)  # let entrance animations settle
                            path = out_dir / f"{screen}-{vp_name}-{i}.png"
                            await page.screenshot(path=str(path))
                            shots.append(str(path))
                        except Exception as e:  # noqa: BLE001 — a missing page should not kill the run
                            print(f"  [media] screenshot failed {url}: {e}")
                    await page.close()
        finally:
            await browser.close()
    return shots


# --------------------------------------------------------------------- remotion
def _remotion_props(bp: Blueprint, shots: list[str], run_id: str, vertical: bool) -> dict:
    """Copies screenshots into remotion/public so staticFile() can load them."""
    pub = REMOTION_DIR / "public" / "runs" / run_id
    pub.mkdir(parents=True, exist_ok=True)
    want = "mobile" if vertical else "desktop"
    by_screen: dict[str, list[str]] = {"app": [], "site": []}
    for s in shots:
        name = Path(s).name
        if f"-{want}-" in name:
            shutil.copy(s, pub / name)
            by_screen[name.split("-")[0]].append(f"runs/{run_id}/{name}")

    scenes = []
    counters = {"app": 0, "site": 0}
    for sc in bp.video.demo_scenes:
        pool = by_screen.get(sc.screen) or by_screen["app"] or by_screen["site"]
        img = pool[counters[sc.screen] % len(pool)] if pool else ""
        counters[sc.screen] += 1
        scenes.append({"title": sc.title, "caption": sc.caption, "image": img})

    c = bp.brand.colors
    return {
        "brandName": bp.brand.name,
        "tagline": bp.brand.tagline,
        "hook": bp.video.hook_line,
        "cta": bp.video.cta_line,
        "colors": {"primary": c.primary, "secondary": c.secondary, "accent": c.accent,
                   "background": c.background, "text": c.text},
        "headingFont": bp.brand.heading_font,
        "scenes": scenes,
    }


async def render_remotion(composition: str, props: dict, out_file: Path) -> bool:
    props_file = out_file.with_suffix(".props.json")
    props_file.write_text(json.dumps(props, indent=2))
    cmd = ["npx", "remotion", "render", "src/index.ts", composition, str(out_file),
           f"--props={props_file}", "--log=error"]
    proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(REMOTION_DIR),
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    out, _ = await proc.communicate()
    if proc.returncode != 0:
        print(f"  [media] remotion {composition} failed:\n{out.decode()[-1500:]}")
        return False
    return out_file.exists()


async def render_still(composition: str, props: dict, out_file: Path, frame: int = 45) -> bool:
    props_file = out_file.with_suffix(".props.json")
    props_file.write_text(json.dumps(props))
    proc = await asyncio.create_subprocess_exec(
        "npx", "remotion", "still", "src/index.ts", composition, str(out_file), f"--frame={frame}",
        f"--props={props_file}", "--log=error", cwd=str(REMOTION_DIR),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    await proc.communicate()
    return proc.returncode == 0 and out_file.exists()


# ----------------------------------------------------------------------- heygen
# Endpoints per HeyGen API v2 docs — verify on first real run.
HEYGEN_GENERATE = "https://api.heygen.com/v2/video/generate"
HEYGEN_STATUS = "https://api.heygen.com/v1/video_status.get"


async def heygen_avatar(settings: Settings, script: str, timeout_s: int = 900) -> str:
    headers = {"X-Api-Key": settings.heygen_key, "Content-Type": "application/json"}
    body = {
        "video_inputs": [{
            "character": {"type": "avatar", "avatar_id": settings.heygen_avatar_id, "avatar_style": "normal"},
            "voice": {"type": "text", "input_text": script[:4500], "voice_id": settings.heygen_voice_id},
        }],
        "dimension": {"width": 1280, "height": 720},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(HEYGEN_GENERATE, headers=headers, json=body)
        r.raise_for_status()
        video_id = r.json()["data"]["video_id"]
        waited = 0
        while waited < timeout_s:
            await asyncio.sleep(15)
            waited += 15
            s = await client.get(HEYGEN_STATUS, headers=headers, params={"video_id": video_id})
            s.raise_for_status()
            data = s.json().get("data", {})
            if data.get("status") == "completed":
                return data.get("video_url", "")
            if data.get("status") == "failed":
                raise RuntimeError(f"HeyGen failed: {data.get('error')}")
    raise TimeoutError("HeyGen video not ready in time")


# ----------------------------------------------------------------------- upload
def upload(settings: Settings, path: Path, run_id: str) -> str:
    import boto3  # optional dependency: pip install '.[s3]'

    s3 = boto3.client("s3", endpoint_url=settings.s3_endpoint or None)
    key = f"{settings.s3_prefix}/{run_id}/{path.name}"
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    s3.upload_file(str(path), settings.s3_bucket, key, ExtraArgs={"ContentType": ctype, "CacheControl": "public, max-age=31536000"})
    return f"{settings.asset_public_base.rstrip('/')}/{key}"


# ------------------------------------------------------------------------- step
async def run_media(state: RunState, settings: Settings) -> MediaResult:
    bp = Blueprint.model_validate(state.output("blueprint"))
    app = state.output("app_build") or {}
    site = state.output("site_build") or {}
    res = MediaResult()
    assets = state.assets_dir
    hosted_hero = (state.output("hero_video") or {}).get("video_url", "")
    if not hosted_hero.startswith("http"):
        hosted_hero = ""  # "FAILED" or empty → Remotion fallback
    if hosted_hero:
        res.public_urls["hero_video"] = hosted_hero
        poster = (state.output("hero_video") or {}).get("poster_url", "")
        if poster:
            res.public_urls["poster_image"] = poster

    app_url = app.get("preview_url") or ""
    site_url = site.get("live_url") or ""
    routes = {"app": [s.route for s in bp.video.demo_scenes if s.screen == "app"] or ["/"],
              "site": ["/"] + [s.route for s in bp.video.demo_scenes if s.screen == "site"]}
    if app_url or site_url:
        res.screenshots = await capture_screenshots({"app": app_url, "site": site_url}, assets, routes)
    else:
        res.skipped.append("screenshots: no app preview_url or site live_url")

    if settings.has_remotion:
        props16 = _remotion_props(bp, res.screenshots, state.run_id, vertical=False)
        props9 = _remotion_props(bp, res.screenshots, state.run_id, vertical=True)
        demo, vert = assets / "demo-16x9.mp4", assets / "demo-9x16.mp4"
        if await render_remotion("ProductDemo", props16, demo):
            res.demo_video = str(demo)
        if await render_remotion("ProductDemoVertical", props9, vert):
            res.demo_video_vertical = str(vert)
        if not hosted_hero:  # Remotion fallback when Higgsfield is off or failed
            hero = assets / "hero-loop.mp4"
            if await render_remotion("HeroLoop", props16, hero):
                res.hero_video = str(hero)
        poster = assets / "hero-poster.png"
        if await render_still("HeroLoop", props16, poster):
            res.poster_image = str(poster)
    else:
        res.skipped.append("remotion: run `npm install` in remotion/ (and have npx on PATH)")

    if settings.has_heygen:
        try:
            res.avatar_video = await heygen_avatar(settings, bp.video.avatar_script)
            res.public_urls["avatar_video"] = res.avatar_video
        except Exception as e:  # noqa: BLE001
            res.skipped.append(f"heygen: {e}")
    else:
        res.skipped.append("heygen: HEYGEN_API_KEY / HEYGEN_AVATAR_ID / HEYGEN_VOICE_ID not set")

    local = {"demo_video": res.demo_video, "demo_video_vertical": res.demo_video_vertical,
             "hero_video": res.hero_video, "poster_image": res.poster_image}
    if settings.has_s3:
        for key, path in local.items():
            if path and key not in res.public_urls:
                try:
                    res.public_urls[key] = await asyncio.to_thread(upload, settings, Path(path), state.run_id)
                except Exception as e:  # noqa: BLE001
                    res.skipped.append(f"upload {key}: {e}")
    elif any(local.values()):
        res.skipped.append("upload: ASSET_S3_BUCKET/ASSET_PUBLIC_BASE_URL not set — videos stay local, "
                           "embed step can only use already-hosted URLs")
    return res
