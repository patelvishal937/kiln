"""recon_site.py — mechanical teardown of a public website.

Given a URL, it collects the *structural* signals an agent needs to rebuild an
ORIGINAL equivalent: information architecture (nav + sitemap), per-page headings
and forms, recurring components, tech-stack fingerprints, JSON-LD, and a colour /
font sample. It does NOT copy proprietary body copy or assets — it records
structure and small samples only. The agent reads recon.json (plus its own
browser screenshots) and writes the judgement-level Teardown.

    python recon_site.py <url> <out_dir> [--max-pages 8]

Only stdlib + httpx are required. If Playwright is installed it is used to read
the rendered DOM (so client-rendered nav/forms are seen); otherwise raw HTML.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

UA = "KilnRecon/0.1 (+structural analysis; respects robots)"

TECH_FINGERPRINTS = {
    "Next.js": [r"/_next/", r"__NEXT_DATA__"],
    "Nuxt": [r"/_nuxt/", r"__NUXT__"],
    "React": [r"react(?:-dom)?(?:\.production)?\.min\.js", r"data-reactroot"],
    "Vue": [r"vue(?:\.runtime)?(?:\.global)?(?:\.prod)?\.js", r"data-v-[0-9a-f]{8}"],
    "Angular": [r"ng-version", r"zone\.js"],
    "Svelte/SvelteKit": [r"svelte-[0-9a-z]+", r"/_app/immutable/"],
    "WordPress": [r"/wp-content/", r"/wp-includes/"],
    "Shopify": [r"cdn\.shopify\.com", r"Shopify\.theme"],
    "Wix": [r"static\.wixstatic\.com", r"wix-?code"],
    "Webflow": [r"assets\.website-files\.com", r"data-wf-page"],
    "Squarespace": [r"static1\.squarespace\.com", r"squarespace\.com"],
    "Tailwind CSS": [r"\b(?:bg|text|flex|grid|rounded|shadow)-[a-z0-9\[\]/.-]+", r"tailwind"],
    "Bootstrap": [r"bootstrap(?:\.min)?\.css", r"class=\"[^\"]*\bcol-(?:xs|sm|md|lg)-"],
    "Stripe": [r"js\.stripe\.com"],
    "Google Analytics / GA4": [r"googletagmanager\.com/gtag", r"google-analytics\.com"],
    "Segment": [r"cdn\.segment\.com"],
    "Intercom": [r"widget\.intercom\.io"],
    "HubSpot": [r"js\.hs-scripts\.com"],
    "Cloudflare": [r"cloudflare"],
}

HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;\"'}]+)", re.I)
GFONT = re.compile(r"fonts\.googleapis\.com/css2?\?family=([^&\"')]+)", re.I)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._cur = None
        self.meta: dict[str, str] = {}
        self.headings: list[tuple[str, str]] = []
        self.links: list[str] = []
        self.forms: list[dict] = []
        self.jsonld: list[str] = []
        self.img_alts = 0
        self.img_total = 0
        self._form: dict | None = None
        self._script_ld = False
        self.inline_style = ""

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._cur = "title"
        elif tag in ("h1", "h2", "h3"):
            self._cur = tag
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img":
            self.img_total += 1
            if a.get("alt"):
                self.img_alts += 1
        elif tag == "form":
            self._form = {"action": a.get("action", ""), "method": a.get("method", "get"), "fields": []}
        elif tag in ("input", "select", "textarea") and self._form is not None:
            self._form["fields"].append(a.get("name") or a.get("type") or tag)
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._script_ld = True
        elif tag == "link" and "stylesheet" in a.get("rel", ""):
            self.links.append(a.get("href", ""))
        if "style" in a:
            self.inline_style += " " + a["style"]

    def handle_endtag(self, tag):
        if tag == "form" and self._form is not None:
            self.forms.append(self._form)
            self._form = None
        if tag == "script":
            self._script_ld = False
        self._cur = None

    def handle_data(self, data):
        if self._cur == "title":
            self.title += data.strip()
        elif self._cur in ("h1", "h2", "h3") and data.strip():
            self.headings.append((self._cur, data.strip()[:120]))
        elif self._script_ld and data.strip():
            self.jsonld.append(data.strip()[:2000])


def fetch(client: httpx.Client, url: str) -> tuple[str, int]:
    try:
        r = client.get(url)
        return r.text, r.status_code
    except Exception as e:  # noqa: BLE001
        return f"<!-- fetch error: {e} -->", 0


def rendered_html(url: str) -> str | None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(user_agent=UA)
            pg.goto(url, wait_until="networkidle", timeout=45000)
            html = pg.content()
            b.close()
            return html
    except Exception as e:  # noqa: BLE001
        print(f"  (playwright render failed, using raw HTML: {e})", file=sys.stderr)
        return None


def same_site(root: str, link: str) -> str | None:
    if not link or link.startswith(("mailto:", "tel:", "#", "javascript:")):
        return None
    absu = urljoin(root, link)
    pr, po = urlparse(root), urlparse(absu)
    if po.netloc and po.netloc != pr.netloc:
        return None
    clean = absu.split("#")[0].rstrip("/")
    return clean or absu


def detect_tech(html: str) -> list[str]:
    found = []
    for name, pats in TECH_FINGERPRINTS.items():
        if any(re.search(p, html) for p in pats):
            found.append(name)
    return found


def sample_design(html: str) -> dict:
    colors = Counter(m.group(0).lower() for m in HEX.finditer(html))
    fonts: Counter = Counter()
    for m in FONT_FAMILY.finditer(html):
        first = m.group(1).split(",")[0].strip().strip("\"'")
        if first and len(first) < 40:
            fonts[first] += 1
    for m in GFONT.finditer(html):
        fonts[m.group(1).split(":")[0].replace("+", " ")] += 3
    return {
        "top_colors": [c for c, _ in colors.most_common(8)],
        "fonts": [f for f, _ in fonts.most_common(6)],
    }


def analyze_page(client: httpx.Client, url: str, use_render: bool) -> dict:
    html = (rendered_html(url) if use_render else None) or fetch(client, url)[0]
    p = PageParser()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001
        pass
    nav = []
    for ln in p.links:
        s = same_site(url, ln)
        if s and not s.endswith((".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff", ".woff2")):
            nav.append(s)
    return {
        "url": url,
        "title": p.title[:140],
        "meta_description": p.meta.get("description", "")[:200],
        "og_image": bool(p.meta.get("og:image")),
        "h1": [t for tag, t in p.headings if tag == "h1"],
        "h2": [t for tag, t in p.headings if tag == "h2"][:12],
        "forms": p.forms,
        "jsonld_types": _ld_types(p.jsonld),
        "img_alt_ratio": round(p.img_alts / p.img_total, 2) if p.img_total else None,
        "internal_links": sorted(set(nav))[:40],
        "tech_signals": detect_tech(html),
        "design_sample": sample_design(html),
    }


def _ld_types(blobs: list[str]) -> list[str]:
    types = []
    for b in blobs:
        for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', b):
            types.append(m.group(1))
    return sorted(set(types))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("out_dir")
    ap.add_argument("--max-pages", type=int, default=8)
    args = ap.parse_args()

    url = args.url if args.url.startswith("http") else f"https://{args.url}"
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": UA}

    with httpx.Client(timeout=30, follow_redirects=True, headers=headers) as client:
        robots, _ = fetch(client, urljoin(url, "/robots.txt"))
        sitemap_urls: list[str] = []
        sm_text, sm_status = fetch(client, urljoin(url, "/sitemap.xml"))
        if sm_status == 200:
            sitemap_urls = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm_text)[:40]

        use_render = rendered_html is not None
        home = analyze_page(client, url, use_render)

        # choose pages to crawl: sitemap first, then homepage nav
        candidates: list[str] = []
        for u in sitemap_urls + home["internal_links"]:
            cu = same_site(url, u)
            if cu and cu not in candidates:
                candidates.append(cu)
        home_clean = url.rstrip("/")
        pages = [home]
        for cu in candidates:
            if len(pages) >= args.max_pages:
                break
            if cu == home_clean:
                continue
            pages.append(analyze_page(client, cu, use_render))

    recon = {
        "source_ref": url,
        "robots_present": bool(robots and "fetch error" not in robots),
        "sitemap_present": bool(sitemap_urls),
        "sitemap_sample": sitemap_urls[:20],
        "page_count_analyzed": len(pages),
        "tech_signals": sorted({t for pg in pages for t in pg["tech_signals"]}),
        "design_sample": home["design_sample"],
        "pages": pages,
    }
    (out / "recon.json").write_text(json.dumps(recon, indent=2))
    print(json.dumps({
        "wrote": str(out / "recon.json"),
        "pages_analyzed": len(pages),
        "tech_signals": recon["tech_signals"],
        "sitemap_present": recon["sitemap_present"],
        "nav": home["internal_links"][:20],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
