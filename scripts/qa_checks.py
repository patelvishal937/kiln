"""Deterministic live checks. The agent fix round only sees what fails here."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from schemas import QACheck, QAResult
from state import RunState


class _Head(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.h1 = 0
        self.videos = 0
        self.forms = 0

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key.lower()] = a.get("content", "")
        elif tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonical = a.get("href", "")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "video" or (tag == "iframe" and re.search(r"youtube|vimeo|heygen", a.get("src", ""))):
            self.videos += 1
        elif tag == "form":
            self.forms += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


async def _check_site(client: httpx.AsyncClient, url: str, expect_video: bool) -> list[QACheck]:
    out: list[QACheck] = []
    t = "site"
    try:
        r = await client.get(url)
    except Exception as e:  # noqa: BLE001
        return [QACheck(target=t, check="reachable", ok=False, detail=f"{url}: {e}")]
    out.append(QACheck(target=t, check="status 200", ok=r.status_code == 200, detail=str(r.status_code)))
    h = _Head()
    h.feed(r.text)
    desc = h.meta.get("description", "")
    out += [
        QACheck(target=t, check="title 10-65 chars", ok=10 <= len(h.title.strip()) <= 65, detail=h.title.strip()[:80]),
        QACheck(target=t, check="meta description 50-160 chars", ok=50 <= len(desc) <= 160, detail=desc[:170]),
        QACheck(target=t, check="og:image present", ok=bool(h.meta.get("og:image"))),
        QACheck(target=t, check="exactly one h1", ok=h.h1 == 1, detail=f"{h.h1} h1 tags (in server HTML)"),
        QACheck(target=t, check="canonical link", ok=bool(h.canonical), detail=h.canonical),
    ]
    if expect_video:
        out.append(QACheck(target=t, check="homepage video embedded", ok=h.videos > 0, detail=f"{h.videos} found"))
    for path in ("/robots.txt", "/sitemap.xml"):
        try:
            rr = await client.get(urljoin(url, path))
            out.append(QACheck(target=t, check=path, ok=rr.status_code == 200 and len(rr.text) > 10, detail=str(rr.status_code)))
        except Exception as e:  # noqa: BLE001
            out.append(QACheck(target=t, check=path, ok=False, detail=str(e)))
    return out


async def _check_app(client: httpx.AsyncClient, preview: str, backend: str) -> list[QACheck]:
    out: list[QACheck] = []
    for label, url in (("app frontend", preview), ("app backend", backend)):
        if not url:
            out.append(QACheck(target="app", check=f"{label} url known", ok=False, detail="missing"))
            continue
        try:
            r = await client.get(url)
            out.append(QACheck(target="app", check=f"{label} responds", ok=r.status_code < 500, detail=f"{r.status_code} {url}"))
        except Exception as e:  # noqa: BLE001
            out.append(QACheck(target="app", check=f"{label} responds", ok=False, detail=f"{url}: {e}"))
    return out


async def run_checks(state: RunState) -> QAResult:
    app = state.output("app_build") or {}
    site = state.output("site_build") or {}
    embed = state.output("embed_media") or {}
    checks: list[QACheck] = []
    async with httpx.AsyncClient(timeout=30, follow_redirects=True,
                                 headers={"User-Agent": "GretaLaunchpadQA/0.1"}) as client:
        if site.get("live_url"):
            checks += await _check_site(client, site["live_url"], expect_video=bool(embed.get("embedded")))
        elif site:
            checks.append(QACheck(target="site", check="published", ok=False, detail=site.get("publish_blocker", "no live_url")))
        if app:
            checks += await _check_app(client, app.get("preview_url", ""), app.get("backend_url", ""))
    return QAResult(checks=checks, still_failing=[f"{c.target}: {c.check} ({c.detail})" for c in checks if not c.ok])
