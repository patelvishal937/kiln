# Phase: site_build — the self-growing marketing website

## Inputs
Brand:
```json
{{brand}}
```
Positioning: {{positioning}}
Pricing: {{pricing}}

Site plan (pages, CTA, the first-turn build prompt):
```json
{{site_plan}}
```
12-week SEO calendar:
```json
{{seo_calendar}}
```
URLs known so far:
```json
{{urls}}
```
Growth settings: timezone `{{timezone}}`, nightly credit limit `{{nightly_limit}}`, tasks per night `{{tasks_per_night}}`. Per-call cap `{{per_call_cap}}`. Run id `{{run_id}}`.

## Tools (Greta MCP, server `greta`)
`create_project`, `send_message`, `get_generation_status`, `get_site_overview`, `publish_site`, `get_growth_plan`, `set_growth_plan`, `list_site_pages`, `add_growth_tasks`, `pull_growth_suggestions`, `get_growth_history`.

## Steps
1. **Prepare the prompt.** Take `site_plan.build_prompt`. Replace every `{APP_URL}` with `urls.app_preview_url`. If that is empty, use `/#signup` and tell the builder the CTA should open a Greta Forms waitlist instead. Check that the prompt states:
   - the pages;
   - the audience;
   - the offer/pricing;
   - lead capture via Greta Forms;
   - the brand hex colours and fonts;
   - "leave room in the home hero for a muted background video".
   
   Add whatever is missing, briefly.
2. **Create.** Call `create_project` with `kind: "self_growing"`, `name: <brand.name>`, and `prompt: <that prompt>`. For self_growing projects the prompt IS the first turn, and the build starts immediately. Save the id and workspace URL with `remember`.
3. **Follow the build.** Poll `get_generation_status`:
   - on `waiting_for_answer`, answer from the inputs (option labels exactly when options are fixed);
   - on `completed`, move on.
   
   If it asks something the inputs cannot settle and the cost of guessing is high, use `ask_human`.
4. **Publish.** Call `get_site_overview`, then `publish_site` (`timeoutSeconds: 120`).
   - Returns `publishing`: poll `get_site_overview` until `liveUrl` / `publishedAt` appear.
   - Returns 402 `FREE_LIMIT_REACHED`: do NOT retry. Set `publish_blocker` and add a human_todo: "Buy a publish cycle with the Publish button: <manageUrl> (<price> credits / <cycleDays> days)".
   - Returns `PENDING_REVIEW`: never use acknowledge. Add a human_todo to review the held changes in the workspace.
   - `live_url` must come from a tool reply, never from a guess.
5. **Growth loop.** Call `set_growth_plan` with `enabled: true`, `hour: 2`, `timezone`, `nightlyCreditLimit: {{nightly_limit}}`, `tasksPerNight: {{tasks_per_night}}`, and do not pass autoApprove.
   - If the reply is `FENN_OWNS_GROWTH`: the site's growth lives in Automatic growth. That is fine: set `growth_authority: "automatic-growth"` and continue.
   - Otherwise set `growth_authority: "nightly-loop"`.
6. **SEO schedule.** Call `list_site_pages`. Drop calendar items the site already covers. Then call `add_growth_tasks` in batches of ≤10, ordered by `week`. Map the fields:

   | calendar | task |
   |---|---|
   | title | title |
   | brief | brief (with `{APP_URL}` replaced) |
   | target_keyword | targetKeyword |
   | search_intent | searchIntent |
   | page_type | pageType |
   | priority | priority |
   | difficulty | difficulty (if set) |

   Count only the tasks that were actually added (not duplicates) in `growth_tasks_added`. If the reply says the tasks went to "Waiting on you" (automatic growth), add a human_todo: "Approve the first SEO drafts in Automatic growth".
7. **Confirm.** Call `get_site_overview` one last time and confirm `growth_loop_enabled` from it, not from what you asked for.

## Output contract (`SiteResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit site_build --file <file>` (SKILL.md has the loop).
