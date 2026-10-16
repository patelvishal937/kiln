"""REPORT.md: what was built, where it lives, what a human still has to do."""

from __future__ import annotations

from state import RunState


def _row(label: str, value: str) -> str:
    return f"| {label} | {value or '—'} |"


def write_report(state: RunState) -> str:
    o = state.output
    brief, bp = o("brief") or {}, o("blueprint") or {}
    app, site = o("app_build") or {}, o("site_build") or {}
    media, embed = o("media") or {}, o("embed_media") or {}
    email, qa, kit = o("email") or {}, o("qa") or {}, o("launch_kit") or {}

    name = (bp.get("brand") or {}).get("name") or brief.get("working_name", state.run_id)
    lines = [
        f"# {name} — launch report",
        "",
        f"Run `{state.run_id}` · idea: {state.idea}",
        "",
        "## Where things live",
        "",
        "| What | Link |",
        "|---|---|",
        _row("App workspace", app.get("workspace_url", "")),
        _row("App preview", app.get("preview_url", "")),
        _row("App backend", app.get("backend_url", "")),
        _row("Site workspace", site.get("workspace_url", "")),
        _row("Site (live)", site.get("live_url", "") or f"not published — {site.get('publish_blocker', '')}"),
        _row("Growth loop", f"{'on' if site.get('growth_loop_enabled') else 'off'}, "
                            f"{site.get('growth_tasks_added', 0)} pages queued ({site.get('growth_authority', '')})"),
    ]
    for k, v in (media.get("public_urls") or {}).items():
        lines.append(_row(k.replace("_", " "), v))
    for k in ("demo_video", "demo_video_vertical", "hero_video", "poster_image"):
        if media.get(k) and k not in (media.get("public_urls") or {}):
            lines.append(_row(f"{k.replace('_', ' ')} (local)", media[k]))

    lines += ["", "## Phases", "", "| Phase | Status | Claude $ | Note |", "|---|---|---|---|"]
    for pname, rec in state.phases.items():
        lines.append(f"| {pname} | {rec.status} | {rec.claude_cost_usd:.2f} | {rec.note[:120]} |")
    lines += ["", f"Greta credits committed (upper bound): **{state.greta_credits_committed:g}**"]

    todos = list(state.human_todos)
    for section in (app, site, embed, email):
        for t in section.get("human_todos", []) or []:
            if t not in todos:
                todos.append(t)
    lines += ["", "## Your to-do list", ""] + ([f"- [ ] {t}" for t in todos] or ["- nothing 🎉"])

    failing = qa.get("still_failing") or []
    lines += ["", "## QA", ""] + ([f"- ❌ {f}" for f in failing] or ["- all live checks passed"])
    if media.get("skipped"):
        lines += ["", "## Skipped", ""] + [f"- {s}" for s in media["skipped"]]
    if email:
        lines += ["", "## Emails", "", f"- templates: {', '.join(email.get('templates', []))}",
                  f"- workflows: {', '.join(email.get('workflows', []))}",
                  f"- test send verified: {email.get('test_send_verified')}"]
        if email.get("integration_snippet"):
            lines += ["", "```", email["integration_snippet"], "```"]
    if kit:
        lines += ["", "## Launch kit", "", f"**Product Hunt:** {kit.get('product_hunt_tagline')}",
                  "", kit.get("product_hunt_description", ""), "", "**X thread**", ""]
        lines += [f"{i + 1}. {t}" for i, t in enumerate(kit.get("x_thread", []))]
        lines += ["", "**LinkedIn**", "", kit.get("linkedin_post", ""), "", "**Cold email**", "", kit.get("cold_email", "")]
    if state.notes:
        lines += ["", "## Agent notes", ""] + [f"- {n}" for n in state.notes]

    text = "\n".join(lines) + "\n"
    (state.dir / "REPORT.md").write_text(text)
    return str(state.dir / "REPORT.md")
