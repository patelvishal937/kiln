---
name: kiln
description: >-
  Turn a product idea — or a teardown of an existing website or APK — into a launched
  product on Greta: a working full-stack app, a self-growing marketing site with an SEO
  schedule, launch videos, onboarding emails and launch copy. Use when the user wants to
  build, clone-and-rebuild, or reverse-engineer a product and ship it. Runs inside this
  Claude Code / Codex session using the connected Greta MCP — no model API key needed.
---

# Kiln

Kiln builds a real product end to end. You are the engine. A local CLI (`scripts/kiln.py`)
holds the state and tells you each step; you do the MCP and web work. Everything a product
needs — app, marketing site, videos, emails, launch copy — comes out of one run.

It works from three starting points:
- **an idea** — `kiln new "<idea>"`
- **a website to rebuild** — `kiln new --from-url <url>` (a `recon` phase tears it down first)
- **an Android app to rebuild** — `kiln new --from-apk <path.apk>` (uses the `apk-reverse` skill)

Reverse-engineering here means **rebuilding an original equivalent**: you map structure,
flows, data and tech, then build a new, re-branded product. You never reuse the original's
name, logo, copy or assets.

## Before you start
- The **Greta MCP must be connected in this session** (`/mcp` in Claude Code, or the Codex
  MCP config). Check with `kiln doctor`.
- First time only, install deps (ask the user to run these — see README):
  `pip install pydantic httpx python-dotenv playwright` and `cd remotion && npm install`.
- For `--from-apk`, the `apk-reverse` skill should be installed:
  `npx skills add newliver666/apk-reverse --skill apk-reverse -y`.

## Run `scripts/kiln.py` as `kiln`
From the kiln directory: `python3 scripts/kiln.py <command>`. (Alias it as `kiln` if you like.)

## The loop — follow it exactly
Repeat until `kiln next` prints `DONE`:

1. **`kiln next`** — prints the next phase, whether it is an *agent phase* or
   *deterministic*, and whether it is a **GATE**.
2. If it is an **agent phase**:
   - **`kiln phase <name>`** — prints the full instructions with the inputs already filled in.
   - Do the work: call the Greta MCP and other tools, and the `kiln` helpers below.
   - Write your result as JSON matching the contract, then **`kiln submit <name> --file result.json`**.
     If it prints validation errors, fix the JSON and submit again.
3. If it is **deterministic** (`media`, `qa`, `report`): just run **`kiln run <name>`**.
4. If the phase is a **GATE** (`intake`, `blueprint`): after submitting, show the user a
   short summary and **wait for their approval** before `kiln next`. If they want changes,
   redo it with `kiln phase <name> --feedback "what to change"`, then submit again.

Do not skip ahead, invent phases, or run a later phase before `kiln next` offers it.

## Helper commands you call during phases
- **`kiln reserve <credits>`** — run this BEFORE every Greta `send_message` / `deploy_project`.
  Nonzero exit means the budget cap is reached: adapt or stop and submit with `open_issues`.
- **`kiln recon-site <url>`** — runs the website analyzer into the run's assets (used in `recon`).
- **`kiln status`**, **`kiln runs`**, **`kiln report`** — inspect state.

## Hard rules (also in references/policy.md — they are not negotiable)
1. **Free Greta deploys only.** Never choose a paid plan; it is a recurring charge. Record it as a human to-do.
2. **Never publish held changes.** Never call `publish_site` with `acknowledge: true`, and never turn on growth `autoApprove`. Those are the owner's decisions.
3. **Every `send_message`/`deploy_project` gets a unique `requestId`**; reuse the same id on a retry so nothing is charged twice.
4. **Stay within the credit caps** via `kiln reserve`.
5. **Verify before you claim.** A build is done / a site is live only when a status read says so.
6. **Rebuilds are original.** Honour each Teardown's `do_not_copy`.

## Map
- `references/phases/` — the instruction for each phase (what `kiln phase` prints).
- `references/policy.md` — the money/safety rules, in full.
- `references/overview.md` — the phase list and what each produces.
- `scripts/` — the CLI, the schemas, the website analyzer, and the deterministic steps.
- `remotion/` — the video compositions (`ProductDemo`, `ProductDemoVertical`, `HeroLoop`).
- `runs/<id>/` — `state.json`, `events.jsonl`, `assets/`, `REPORT.md`.
