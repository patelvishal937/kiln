# Kiln

Turn a product **idea** — or a teardown of an **existing website or Android app** — into a
launched product on Greta: a working full-stack app, a self-growing marketing site with an
SEO schedule, launch videos, onboarding emails, and launch copy.

Kiln runs **inside your Claude Code / Codex session**. There is no model API key: the agent
in the terminal is the model, and it drives the Greta MCP (and any other MCP servers you
have connected) through a small local state machine, `scripts/kiln.py`. The full procedure
is in [SKILL.md](SKILL.md); the phases are in [references/overview.md](references/overview.md).

## What it produces
1. Full-stack app (auth, DB, deployed) — Greta `full_stack`
2. Self-growing marketing site + 12-week SEO/AEO schedule — Greta `self_growing`
3. Demo video (16:9 + 9:16) and a homepage hero loop — Remotion / Higgsfield / HeyGen
4. Onboarding email sequence — Volanea
5. Live QA with one fix round
6. Launch kit (Product Hunt, X, LinkedIn, Reddit, cold email) + `REPORT.md`

## Reverse-engineer and rebuild
- `kiln new --from-url <url>` — a `recon` phase runs the website analyzer
  (`scripts/recon_site.py`: IA, forms, tech fingerprints, design sample) plus a browser
  pass, and writes a structured **Teardown**.
- `kiln new --from-apk <path>` — `recon` uses the installed
  [`apk-reverse`](https://github.com/newliver666/apk-reverse) skill as its extraction engine
  (see [references/reverse-apk.md](references/reverse-apk.md)).

In both cases Kiln builds an **original, re-branded** product from the structure — never the
original's name, logo, copy or assets (see [references/policy.md](references/policy.md)).

## Setup (run these yourself)
```bash
cd kiln && python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[recon,s3]'
playwright install chromium
cd remotion && npm install && cd ..
cp .env.example .env          # budgets + optional HeyGen/S3; no API key needed
```
Connect the Greta MCP in this session (Claude Code `/mcp`, or your Codex MCP config), then:
```bash
python3 scripts/kiln.py doctor
```
Tip: `alias kiln="python3 $PWD/scripts/kiln.py"`.

## Use
```bash
kiln new "invoicing app for freelance designers that chases late payments"
# or:  kiln new --from-url https://some-saas.com
# or:  kiln new --from-apk ~/Downloads/app.apk
kiln next        # then follow what it prints — phase / submit / run — until DONE
kiln status
```

## How it fits together
| Piece | File |
|---|---|
| Procedure the agent follows | `SKILL.md` |
| State machine, phase routing, gates, validation | `scripts/kiln.py` |
| Hard money/safety rules | `references/policy.md` |
| Typed result per phase | `scripts/schemas.py` |
| Per-phase instructions (what `kiln phase` prints) | `references/phases/` |
| Website teardown analyzer | `scripts/recon_site.py` |
| Screenshots → Remotion → HeyGen → S3 | `scripts/media_steps.py` |
| Live QA checks | `scripts/qa_checks.py` |
| Video compositions | `remotion/src/` |

Each run lives in `runs/<id>/` (`state.json`, `events.jsonl`, `assets/`, `REPORT.md`).
Preview the videos with sample props: `cd remotion && npm run studio`.

Plan: `../feature_plans/kiln_plan_2026-10-16.md`.
