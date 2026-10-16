# Kiln

**Turn a product idea — or a teardown of an existing website or Android app — into a launched product.**

Kiln is a build engine that runs **inside your Claude Code or Codex session**. You give it an idea (or point it at a product to rebuild), and it walks the whole path to launch: a working full-stack app, a self-growing marketing website with an SEO schedule, launch videos, onboarding emails, and launch copy — all built on the [Greta](https://greta.sh) MCP.

There is **no model API key**. The agent in your terminal *is* the model; Kiln is a lightweight state machine (`scripts/kiln.py`) that tells the agent what to do at each step and drives the Greta MCP tools your session already has connected.

```
idea ──►  intake → research → blueprint → app → site → videos → emails → QA → launch kit → report
url  ──►  + reverse-engineer teardown first
apk  ──►  + reverse-engineer teardown first (via the apk-reverse skill)
```

---

## What you get out of one run

| Output | Built with |
| --- | --- |
| Full-stack app — auth, database, deployed backend | Greta `full_stack` |
| Marketing website + 12-week SEO/AEO content schedule that keeps growing | Greta `self_growing` |
| Product demo video (16:9 and 9:16) + a homepage hero loop | Remotion (local), Higgsfield, HeyGen |
| Onboarding email sequence | Volanea |
| Live QA (SEO + reachability) with one automatic fix round | built-in |
| Launch kit — Product Hunt, X thread, LinkedIn, Reddit, cold email | built-in |
| `REPORT.md` — every URL, asset, and the to-dos left for you | built-in |

Greta is required. Everything else (Higgsfield, HeyGen, Volanea, Apify, S3) is optional and skipped cleanly if it isn't connected.

---

## Requirements

- **Claude Code** or **Codex** — Kiln runs as an agent skill inside one of these.
- **The Greta MCP connected in that session.** This is the only required integration. (Claude Code: `/mcp`; Codex: its MCP config.)
- **Python 3.10+**
- **Node.js 18+** — only if you want videos rendered locally (Remotion).

---

## Install

```bash
git clone https://github.com/patelvishal937/kiln.git
cd kiln

python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[recon,s3]'      # 'recon' = website analysis + screenshots, 's3' = video hosting
playwright install chromium       # for screenshots / rendered-DOM teardown

cd remotion && npm install && cd ..   # optional: only if you want rendered videos

cp .env.example .env               # budgets + optional HeyGen/S3 — no model API key needed
```

Then connect the **Greta MCP** in your Claude Code / Codex session and verify your setup:

```bash
python3 scripts/kiln.py doctor
```

Optional convenience alias:

```bash
alias kiln="python3 $PWD/scripts/kiln.py"
```

> **Reverse-engineering an APK?** Also install the [`apk-reverse`](https://github.com/newliver666/apk-reverse) skill — Kiln uses it as the extraction engine:
> `npx skills add newliver666/apk-reverse --skill apk-reverse -y`

---

## Usage

Start a run from any of three entry points:

```bash
kiln new "invoicing app for freelance designers that chases late payments"   # from an idea
kiln new --from-url https://some-saas.com                                    # rebuild a website
kiln new --from-apk ~/Downloads/app.apk                                      # rebuild an Android app
```

Then just follow the prompts — Kiln tells you exactly what to do next:

```bash
kiln next
```

### The loop

`kiln next` prints the next phase and what kind it is. You repeat this until it says `DONE`:

1. **`kiln next`** — names the next phase, whether it's an *agent phase* or *deterministic*, and whether it's a **gate**.
2. **Agent phase:**
   - `kiln phase <name>` — prints the full instructions with your run's data already filled in.
   - You do the work (calling the Greta MCP and other tools).
   - `kiln submit <name> --file result.json` — validates and saves your result. If it reports errors, fix the JSON and submit again.
3. **Deterministic phase** (`media`, `qa`, `report`): just run `kiln run <name>`.
4. **Gate** (`intake`, `blueprint`): after submitting, the run pauses so you can review and approve before continuing. Want changes? Redo it with `kiln phase <name> --feedback "what to change"`.

Other commands: `kiln status`, `kiln runs`, `kiln report`, and `kiln reserve <credits>` (the credit check before each Greta spend).

---

## The phases

| # | Phase | Kind | Produces |
| --- | --- | --- | --- |
| 1 | `intake` | agent · **gate** | the brief |
| 2 | `recon` | agent | teardown *(only for `--from-url` / `--from-apk`)* |
| 3 | `research` | agent | competitors, customer pains, keyword ideas |
| 4 | `blueprint` | agent · **gate** | brand, app spec, site plan, SEO calendar, video + email plans |
| 5 | `app_build` | agent | the full-stack app, built milestone-by-milestone, deployed |
| 6 | `site_build` | agent | the marketing site, published, growth loop on, SEO queued |
| 7 | `hero_video` | agent | homepage background loop (Higgsfield → Remotion fallback) |
| 8 | `media` | deterministic | screenshots → demo videos → avatar → hosting |
| 9 | `embed_media` | agent | videos placed on the homepage |
| 10 | `email` | agent | onboarding email sequence |
| 11 | `qa` | deterministic | live SEO + reachability checks |
| 12 | `qa_fix` | agent | one round of fixes *(only if QA found issues)* |
| 13 | `launch_kit` | agent | launch copy for every channel |
| 14 | `report` | deterministic | `REPORT.md` |

See [`references/overview.md`](references/overview.md) for the detail.

---

## Reverse-engineer and rebuild

Point Kiln at an existing product and it produces a structured **Teardown** — the product's jobs, information architecture, screens, flows, data entities, tech stack and design language — then builds an **original, re-branded** equivalent from that structure.

- **Website:** `scripts/recon_site.py` fetches the site (and, with Playwright, its rendered DOM), and extracts the IA, forms, tech fingerprints (Next.js, Shopify, Tailwind, Stripe, …), JSON-LD, and a colour/font sample into `recon.json`. The agent adds a browser pass and writes the Teardown.
- **APK:** the `recon` phase drives the [`apk-reverse`](https://github.com/newliver666/apk-reverse) skill and turns its findings into the same Teardown. See [`references/reverse-apk.md`](references/reverse-apk.md).

**Kiln builds originals, not clones.** Every Teardown carries a `do_not_copy` list. Kiln reproduces structure and ideas under a **new name with new branding, copy and assets** — never the original's trademarks, logos or verbatim text. Only analyze a product you're entitled to study.

---

## Configuration

`.env` (copied from `.env.example`) configures the Python helper scripts and the budget policy. **No model API key is involved.**

| Variable | Purpose |
| --- | --- |
| `RUN_CREDIT_CAP`, `PER_CALL_CREDIT_CAP` | Greta credit limits the agent is held to |
| `GROWTH_NIGHTLY_CREDIT_LIMIT`, `GROWTH_TASKS_PER_NIGHT`, `TIMEZONE` | the site's nightly growth loop |
| `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` | optional avatar explainer video |
| `ASSET_S3_*`, `ASSET_PUBLIC_BASE_URL` | optional hosting so rendered videos can be embedded on the site |

---

## Safety & spending

Kiln enforces hard rules so an automated run can't quietly cost you money or ship something unreviewed (full list in [`references/policy.md`](references/policy.md)):

- **Free Greta deploys only** — paid plans are recurring and become a to-do for you, never auto-selected.
- **Credit caps** via `kiln reserve` before every Greta spend; a unique `requestId` on each so retries are never double-charged.
- **Never publishes unreviewed changes** and **never enables growth auto-approve** — those stay your decision.
- **Verifies before claiming** — a build is "done" only when a status read says so.

---

## Project structure

```
kiln/
├── SKILL.md              the procedure the agent follows
├── scripts/
│   ├── kiln.py            state machine / CLI
│   ├── recon_site.py      website teardown analyzer
│   ├── schemas.py         typed result per phase
│   ├── state.py · config.py · render_prompt.py
│   └── media_steps.py · qa_checks.py · report_build.py
├── references/
│   ├── overview.md · policy.md · reverse-apk.md
│   └── phases/            one instruction file per phase
├── remotion/             video compositions (ProductDemo, ProductDemoVertical, HeroLoop)
└── runs/<id>/            per-run state.json, events.jsonl, assets/, REPORT.md
```

Preview the video compositions with sample data: `cd remotion && npm run studio`.

---

## Status

Core engine complete and self-tested (the full `kiln` loop, credit caps, validation, phase routing, all phase prompts, and both reverse-engineer entry points). A full live end-to-end run against Greta — and verification of the HeyGen/Higgsfield/Volanea paths — is the next step and depends on those integrations being connected in your session.

## License

MIT — see [LICENSE](LICENSE).
