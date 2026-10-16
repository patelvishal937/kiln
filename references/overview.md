# Kiln phases

The full pipeline. `kiln next` walks it, skipping phases that don't apply.

| # | Phase | Kind | Produces | Notes |
|---|---|---|---|---|
| 1 | intake | agent · **gate** | Brief | Frames the product. For reverse runs, also sets what to keep/change/improve. |
| 2 | recon | agent | Teardown | Only for `--from-url` / `--from-apk`. Maps the existing product's structure. |
| 3 | research | agent | Research | Competitors, customer pains, 15–30 keyword ideas. |
| 4 | blueprint | agent · **gate** | Blueprint | Brand, app spec (as build milestones), site plan, 12-week SEO calendar, video scripts, emails. The single source of truth. |
| 5 | app_build | agent | AppResult | Greta `full_stack`: build milestone-by-milestone, deploy free. |
| 6 | site_build | agent | SiteResult | Greta `self_growing`: publish, turn on nightly growth, queue the SEO calendar. |
| 7 | hero_video | agent | HeroVideoResult | Higgsfield background loop. Falls back to the Remotion `HeroLoop` if absent. |
| 8 | media | deterministic | MediaResult | Playwright screenshots → Remotion `ProductDemo` (16:9 + 9:16) → HeyGen avatar → S3 upload. |
| 9 | embed_media | agent | EmbedResult | Puts the hosted videos on the homepage, republishes. |
| 10 | email | agent | EmailResult | Volanea onboarding sequence, test-sent. |
| 11 | qa | deterministic | QAResult | Live SEO + reachability checks on the real URLs. |
| 12 | qa_fix | agent | QAFixResult | Only if QA found failures. One fix round, then re-verify. |
| 13 | launch_kit | agent | LaunchKit | Product Hunt, X thread, LinkedIn, Reddit, cold email, short-video captions. |
| 14 | report | deterministic | REPORT.md | Links, to-dos, QA, launch copy. |

Gates (1, 4) stop for the user's approval. Optional integrations (Apify, Higgsfield, HeyGen,
Volanea, S3) degrade cleanly — the phase records why it skipped and moves on.

## Starting points
- `kiln new "<idea>"` → skips recon.
- `kiln new --from-url <url>` → recon runs the website analyzer + browser pass → Teardown.
- `kiln new --from-apk <path>` → recon drives the `apk-reverse` skill → Teardown.

In every case the output is an **original** product; see references/policy.md §9.
