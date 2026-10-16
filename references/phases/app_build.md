# Phase: app_build — build and deploy the full-stack app on Greta

## Inputs
Brand:
```json
{{brand}}
```
App spec (data models, pages, milestones, acceptance checks):
```json
{{app_spec}}
```
Pricing: {{pricing}}

Per-call credit cap: {{per_call_cap}} · Run id: `{{run_id}}`

## Tools (Greta MCP, server `greta`)
`create_project`, `send_message`, `get_generation_status`, `get_project`, `render_project`, `deploy_project`, `get_deployment_status`, `get_credits`.

## Steps
1. **Check credits.** Call `get_credits` once. If the balance looks too small for ~4 build turns + a deploy, still proceed, but note it in `open_issues`.
2. **Create.** Call `create_project` with `kind: "full_stack"` and `name: <brand.name>`. A full_stack project is created EMPTY: the prompt is not consumed. Save the id with `remember`.
3. **Build, one milestone at a time.** For milestone i (1-based):
   - Message = the milestone text, prefixed on milestone 1 with a short header covering: the product name, one-line summary, brand colours (hex) + fonts, "use these consistently across the app".
   - Call `send_message` with `requestId: "{{run_id}}-app-m<i>"`, `creditBudget` between 8 and {{per_call_cap}} (bigger milestones need more), and `timeoutSeconds: 60`.
   - If the reply is `generating`: poll `get_generation_status` until it is completed. Space your polls by doing nothing else in between; each poll is one call.
   - If it is `waiting_for_answer`: answer from the spec (option labels exactly when options are fixed), then keep polling.
   - If it is `completed_no_changes`: the work was NOT done. Send ONE sharper retry with `requestId: "{{run_id}}-app-m<i>-r1"` that names the exact files, routes and components expected. If that also fails, record it in `open_issues` and move on.
   - If a policy denial says the credit cap is reached: stop building and go to step 5.
   - Record finished milestones in `milestones_completed`.
4. **Deploy.** Call `deploy_project` with `planId: "free"`, `requestId: "{{run_id}}-deploy"`, `timeoutSeconds: 120`. If it returns `deploying`, poll `get_deployment_status` with the deploymentId. Record `backend_url` and `deployment_id`.
   - If the free-cycle limit is hit, do NOT pick a paid plan. Add a human_todo: "Free deploy cycles used up — choose a plan in the Greta workspace (<workspace url>)".
5. **Find the URLs.** Use `get_project` (and `render_project` if needed) for `workspace_url` and the frontend `preview_url`. Do not guess URLs.
6. **Acceptance.** For each acceptance check, judge from the latest build summaries / changed files whether it is implemented. Status is one of: `implemented`, `partial`, or `not found`. You cannot click in a browser here, so do not claim "tested". QA runs live checks later.

## Rules
- One project only. Never create a second one to "start fresh".
- Do not send the whole spec in one giant message. Milestones exist because large single turns produce shallow apps.
- Do not ask the builder to change stacks or frameworks. Its defaults are fine.

## Output contract (`AppResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit app_build --file <file>` (SKILL.md has the loop).
