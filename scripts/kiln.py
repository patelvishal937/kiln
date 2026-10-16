#!/usr/bin/env python3
"""kiln — the local state machine an agent (Claude Code / Codex) drives to build a product.

No model API key: the agent in the terminal is the model, and the MCP servers are
whatever the session has connected. This CLI only holds run state, prints the filled
instructions for each phase, validates what the agent submits, runs the deterministic
Python steps (screenshots, Remotion, QA, report), and enforces the credit policy.

Commands:
  kiln doctor
  kiln new "<idea>"                 start from an idea
  kiln new --from-url <url>         reverse-engineer a website, then rebuild
  kiln new --from-apk <path>        reverse-engineer an APK, then rebuild
  kiln next                         what phase to run next (or DONE)
  kiln phase <name>                 print the filled instructions for a phase
  kiln submit <name> --file <f>     validate + save a phase result (reads stdin if no --file)
  kiln run <name>                   execute a deterministic phase (media | qa | report)
  kiln reserve <credits>            policy check before a Greta spend (nonzero exit = refused)
  kiln recon-site <url>             run the website analyzer into the current run
  kiln status [run_id] | kiln runs | kiln report [run_id]

Most commands act on the current run; pass --run <id> to target another.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import schemas as S  # noqa: E402
from config import REMOTION_DIR, RUNS_DIR, Settings  # noqa: E402
from render_prompt import render, schema_text  # noqa: E402
from state import RunState, _set_current  # noqa: E402

SETTINGS = Settings()


# --------------------------------------------------------------- phase registry
def _brief(st: RunState) -> dict:
    return st.output("brief") or {}


def _bp(st: RunState) -> dict:
    return st.output("blueprint") or {}


def _teardown(st: RunState) -> Any:
    return st.output("recon") or "(none)"


def _urls(st: RunState) -> dict:
    app, site = st.output("app_build") or {}, st.output("site_build") or {}
    return {"app_preview_url": app.get("preview_url", ""), "app_backend_url": app.get("backend_url", ""),
            "site_live_url": site.get("live_url", ""), "app_workspace_url": app.get("workspace_url", ""),
            "site_workspace_url": site.get("workspace_url", "")}


def _wants(flag: str):
    return lambda st: (bool(_brief(st).get(flag, True)), f"brief has {flag}=false")


def _done(phase: str):
    return lambda st: (bool(st.output(phase)), f"{phase} not done")


def _all(*fns):
    def chk(st: RunState):
        for f in fns:
            ok, why = f(st)
            if not ok:
                return False, why
        return True, ""
    return chk


class Phase:
    def __init__(self, name, title, *, schema=None, context=None, gate=False,
                 deterministic=False, enabled=lambda st: (True, "")):
        self.name, self.title, self.schema = name, title, schema
        self.context, self.gate = context, gate
        self.deterministic, self.enabled = deterministic, enabled


PHASES: list[Phase] = [
    Phase("intake", "Understand the idea / product", schema=S.Brief, gate=True,
          context=lambda st: {"idea": st.idea, "auto_mode": st.auto,
                              "source_kind": st.source_kind, "source_ref": st.source_ref or "(none)"}),
    Phase("recon", "Reverse-engineer the existing product", schema=S.Teardown,
          enabled=lambda st: (st.source_kind in ("website", "apk"), "source is a fresh idea"),
          context=lambda st: {"brief": _brief(st), "source_kind": st.source_kind,
                              "source_ref": st.source_ref}),
    Phase("research", "Market & keyword research", schema=S.Research,
          context=lambda st: {"brief": _brief(st), "teardown": _teardown(st),
                              "apify_available": "check your connected MCP servers — use Apify tools if present, else web search"}),
    Phase("blueprint", "Blueprint (brand, app, site, SEO, video, email)", schema=S.Blueprint, gate=True,
          context=lambda st: {"brief": _brief(st), "research": st.output("research") or {}, "teardown": _teardown(st)}),
    Phase("app_build", "Build + deploy the full-stack app (Greta)", schema=S.AppResult,
          enabled=_wants("wants_app"),
          context=lambda st: {"brand": _bp(st).get("brand", {}), "app_spec": _bp(st).get("app", {}),
                              "pricing": _bp(st).get("pricing", ""), "per_call_cap": SETTINGS.per_call_credit_cap}),
    Phase("site_build", "Build + publish the self-growing site (Greta)", schema=S.SiteResult,
          enabled=_wants("wants_site"),
          context=lambda st: {"brand": _bp(st).get("brand", {}), "site_plan": _bp(st).get("site", {}),
                              "positioning": _bp(st).get("positioning", ""), "pricing": _bp(st).get("pricing", ""),
                              "seo_calendar": _bp(st).get("seo_calendar", []), "urls": _urls(st),
                              "timezone": SETTINGS.timezone, "nightly_limit": SETTINGS.growth_nightly_credit_limit,
                              "tasks_per_night": SETTINGS.growth_tasks_per_night, "per_call_cap": SETTINGS.per_call_credit_cap}),
    Phase("hero_video", "Hero loop video (Higgsfield, optional)", schema=S.HeroVideoResult,
          enabled=_wants("wants_videos"),
          context=lambda st: {"brand": _bp(st).get("brand", {}), "video_plan": _bp(st).get("video", {})}),
    Phase("media", "Screenshots, Remotion renders, HeyGen avatar", schema=S.MediaResult,
          deterministic=True, enabled=_wants("wants_videos")),
    Phase("embed_media", "Put videos on the homepage", schema=S.EmbedResult,
          enabled=_all(_done("site_build"), _done("media"),
                       lambda st: (bool((st.output("media") or {}).get("public_urls")),
                                   "no hosted video URLs (set S3 vars, or connect Higgsfield/HeyGen)")),
          context=lambda st: {"site": st.output("site_build") or {}, "media": st.output("media") or {},
                              "brand": _bp(st).get("brand", {}), "per_call_cap": SETTINGS.per_call_credit_cap}),
    Phase("email", "Onboarding emails (Volanea, optional)", schema=S.EmailResult,
          enabled=_wants("wants_emails"),
          context=lambda st: {"brand": _bp(st).get("brand", {}), "emails": _bp(st).get("emails", []), "urls": _urls(st)}),
    Phase("qa", "Live QA checks", schema=S.QAResult, deterministic=True),
    Phase("qa_fix", "Fix failing live checks", schema=S.QAFixResult,
          enabled=lambda st: (bool((st.output("qa") or {}).get("still_failing")), "QA had no failures"),
          context=lambda st: {"failing": (st.output("qa") or {}).get("still_failing", []),
                              "app": st.output("app_build") or {}, "site": st.output("site_build") or {},
                              "blueprint_site": _bp(st).get("site", {})}),
    Phase("launch_kit", "Launch kit copy", schema=S.LaunchKit,
          context=lambda st: {"brief": _brief(st), "blueprint": _bp(st), "urls": _urls(st),
                              "research": st.output("research") or {}}),
    Phase("report", "Write REPORT.md", deterministic=True),
]
BY_NAME = {p.name: p for p in PHASES}


# --------------------------------------------------------------------- helpers
def _load(run: str | None) -> RunState:
    return RunState.load(run) if run else RunState.current()


def _phase_status(st: RunState, p: Phase) -> str:
    rec = st.phases.get(p.name)
    return rec.status if rec else "pending"


def _next_phase(st: RunState) -> Phase | None:
    for p in PHASES:
        rec = st.phases.get(p.name)
        if rec and rec.status in ("done", "skipped"):
            continue
        ok, why = p.enabled(st)
        if not ok:
            st.phase(p.name).status = "skipped"
            st.phase(p.name).note = why
            st.save()
            continue
        return p
    return None


# -------------------------------------------------------------------- commands
def cmd_doctor(args) -> int:
    print("Kiln — environment check\n")
    print("Integrations (for the Python helper scripts):")
    for k, v in SETTINGS.integrations_summary().items():
        print(f"  {'OK ' if v else '-- '} {k}")
    try:
        import pydantic  # noqa: F401
        print("  OK  pydantic")
    except ImportError:
        print("  --  pydantic  (pip install pydantic httpx python-dotenv)")
    if not (REMOTION_DIR / "node_modules").exists():
        print(f"  --  remotion   (cd {REMOTION_DIR} && npm install)")
    print("\nGreta MCP: this must be connected in THIS session (Claude Code /mcp or Codex config).")
    print(f"           target from .env: {SETTINGS.greta_url}")
    print("APK reverse: optional skill — npx skills add newliver666/apk-reverse --skill apk-reverse -y")
    return 0


def cmd_new(args) -> int:
    if args.from_url:
        st = RunState.new(args.from_url, args.auto, "website", args.from_url)
    elif args.from_apk:
        st = RunState.new(Path(args.from_apk).name, args.auto, "apk", args.from_apk)
    elif args.idea:
        st = RunState.new(args.idea, args.auto, "idea", "")
    else:
        print("Give an idea, --from-url <url>, or --from-apk <path>", file=sys.stderr)
        return 2
    print(f"Started run: {st.run_id}  ({st.source_kind})")
    print(f"State: {st.dir}/state.json")
    print("\nNow run:  kiln next")
    return 0


def cmd_next(args) -> int:
    st = _load(args.run)
    p = _next_phase(st)
    if p is None:
        print("DONE — all phases complete or skipped. See the report:")
        rp = st.output("report") or {}
        print(f"  {rp.get('path', st.dir / 'REPORT.md')}")
        return 0
    kind = "deterministic (run it)" if p.deterministic else "agent phase"
    print(f"NEXT: {p.name}   [{kind}]{'   *** GATE: stop for user approval after submit ***' if p.gate else ''}")
    print(f"  {p.title}")
    if p.deterministic:
        print(f"\n  → kiln run {p.name}")
    else:
        print(f"\n  → kiln phase {p.name}        (read the instructions)")
        print(f"  → do the work, then: kiln submit {p.name} --file <result.json>")
    return 0


def cmd_phase(args) -> int:
    st = _load(args.run)
    p = BY_NAME.get(args.name)
    if not p or p.deterministic:
        print(f"{args.name} is not an agent phase. Use `kiln run {args.name}`." if p else f"Unknown phase {args.name}", file=sys.stderr)
        return 2
    ctx = dict(p.context(st)) if p.context else {}
    ctx["output_schema"] = schema_text(p.schema)
    ctx["run_id"] = st.run_id
    ctx["feedback"] = args.feedback or "(none)"
    prev = st.phases.get(p.name)
    ctx["previous_output"] = (prev.output if (prev and args.feedback and prev.output) else "(first attempt)")
    print(render("system", run_id=st.run_id, phase=p.name))
    print("\n" + "=" * 78 + "\n")
    print(render(p.name, **ctx))
    return 0


def cmd_submit(args) -> int:
    st = _load(args.run)
    p = BY_NAME.get(args.name)
    if not p or not p.schema:
        print(f"Cannot submit to {args.name}.", file=sys.stderr)
        return 2
    raw = Path(args.file).read_text() if args.file else sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"INVALID JSON: {e}\nFix it and submit again.", file=sys.stderr)
        return 1
    try:
        model = p.schema.model_validate(data)
    except Exception as e:  # pydantic ValidationError
        print(f"VALIDATION FAILED — fix these and submit again:\n{e}", file=sys.stderr)
        return 1
    rec = st.phase(p.name)
    rec.output, rec.status, rec.attempts = model.model_dump(), "done", rec.attempts + 1
    # propagate the source fields the intake brief captured
    if p.name == "intake":
        st.source_kind = rec.output.get("source_kind", st.source_kind) or st.source_kind
        st.source_ref = rec.output.get("source_ref", st.source_ref) or st.source_ref
    st.add_todos(rec.output.get("human_todos", []) if isinstance(rec.output, dict) else [])
    st.save()
    _set_current(st.run_id)
    print(f"OK — {p.name} saved.")
    if p.gate:
        print("\n*** GATE: show the user a short summary of this result and WAIT for their approval")
        print("    before running `kiln next`. If they want changes, redo this phase with")
        print(f"    `kiln phase {p.name} --feedback \"...\"`. ***")
    else:
        print("Run `kiln next` for the next phase.")
    return 0


def cmd_run(args) -> int:
    st = _load(args.run)
    p = BY_NAME.get(args.name)
    if not p or not p.deterministic:
        print(f"{args.name} is not a deterministic phase (use `kiln phase`).", file=sys.stderr)
        return 2
    rec = st.phase(p.name)
    rec.status = "running"
    st.save()
    try:
        if p.name == "media":
            from media_steps import run_media
            result = asyncio.run(run_media(st, SETTINGS))
            rec.output = result.model_dump()
        elif p.name == "qa":
            result = asyncio.run(_run_qa(st))
            rec.output = result.model_dump()
        elif p.name == "report":
            from report_build import write_report
            rec.output = {"path": write_report(st)}
    except Exception as e:  # noqa: BLE001
        rec.status, rec.note = "failed", f"{type(e).__name__}: {e}"[:400]
        st.save()
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    rec.status = "done"
    st.add_todos(rec.output.get("human_todos", []) if isinstance(rec.output, dict) else [])
    st.save()
    print(f"OK — {p.name} done.")
    if p.name == "qa" and rec.output.get("still_failing"):
        print(f"{len(rec.output['still_failing'])} checks failing:")
        for f in rec.output["still_failing"]:
            print(f"  - {f}")
        print("`kiln next` will offer the qa_fix phase.")
    print("Run `kiln next`.")
    return 0


async def _run_qa(st: RunState):
    from qa_checks import run_checks
    return await run_checks(st)


def cmd_reserve(args) -> int:
    st = _load(args.run)
    ok, msg = st.reserve_credits(float(args.credits), SETTINGS.per_call_credit_cap, SETTINGS.run_credit_cap)
    print(("OK — " if ok else "REFUSED — ") + msg, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


def cmd_recon_site(args) -> int:
    st = _load(args.run)
    url = args.url or st.source_ref
    if not url:
        print("No URL (pass one or start the run with --from-url).", file=sys.stderr)
        return 2
    script = Path(__file__).resolve().parent / "recon_site.py"
    out_dir = st.assets_dir / "recon"
    print(f"Analyzing {url} → {out_dir} ...")
    rc = subprocess.run([sys.executable, "-I", str(script), url, str(out_dir), "--max-pages", str(args.max_pages)])
    return rc.returncode


def cmd_status(args) -> int:
    st = _load(args.run_id)
    print(f"{st.run_id}  ({st.source_kind}{': ' + st.source_ref if st.source_ref else ''})")
    print(f"idea: {st.idea}\n")
    for p in PHASES:
        rec = st.phases.get(p.name)
        print(f"  {p.name:12} {(rec.status if rec else 'pending'):9} {(rec.note[:70] if rec else '')}")
    print(f"\nGreta credits committed: {st.greta_credits_committed:g} / {SETTINGS.run_credit_cap:g}")
    if st.human_todos:
        print("To-do:")
        for t in st.human_todos:
            print(f"  - {t}")
    return 0


def cmd_runs(args) -> int:
    for d in sorted(RUNS_DIR.glob("*/state.json")):
        data = json.loads(d.read_text())
        print(f"{data['run_id']:46} [{data.get('source_kind','idea')}] {data['idea'][:48]}")
    return 0


def cmd_report(args) -> int:
    st = _load(args.run_id)
    from report_build import write_report
    path = write_report(st)
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="kiln", description="Build a product from an idea or a teardown.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)

    n = sub.add_parser("new")
    n.add_argument("idea", nargs="?")
    n.add_argument("--from-url")
    n.add_argument("--from-apk")
    n.add_argument("--auto", action="store_true")
    n.set_defaults(fn=cmd_new)

    for name, fn in (("next", cmd_next),):
        pr = sub.add_parser(name)
        pr.add_argument("--run")
        pr.set_defaults(fn=fn)

    ph = sub.add_parser("phase")
    ph.add_argument("name")
    ph.add_argument("--run")
    ph.add_argument("--feedback")
    ph.set_defaults(fn=cmd_phase)

    sb = sub.add_parser("submit")
    sb.add_argument("name")
    sb.add_argument("--file")
    sb.add_argument("--run")
    sb.set_defaults(fn=cmd_submit)

    rn = sub.add_parser("run")
    rn.add_argument("name")
    rn.add_argument("--run")
    rn.set_defaults(fn=cmd_run)

    rs = sub.add_parser("reserve")
    rs.add_argument("credits")
    rs.add_argument("--run")
    rs.set_defaults(fn=cmd_reserve)

    rc = sub.add_parser("recon-site")
    rc.add_argument("url", nargs="?")
    rc.add_argument("--run")
    rc.add_argument("--max-pages", type=int, default=8)
    rc.set_defaults(fn=cmd_recon_site)

    stt = sub.add_parser("status")
    stt.add_argument("run_id", nargs="?")
    stt.set_defaults(fn=cmd_status)

    sub.add_parser("runs").set_defaults(fn=cmd_runs)

    rp = sub.add_parser("report")
    rp.add_argument("run_id", nargs="?")
    rp.set_defaults(fn=cmd_report)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
