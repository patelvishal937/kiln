# Phase: qa_fix — one round of fixes for failing live checks

## Failing checks (from automated HTTP checks of the live URLs)
```json
{{failing}}
```
App:
```json
{{app}}
```
Site:
```json
{{site}}
```
Site plan:
```json
{{blueprint_site}}
```
Run id `{{run_id}}`

## Tools
Greta MCP (`send_message`, `get_generation_status`, `get_site_overview`, `publish_site`, `get_project`, `get_deployment_status`), plus WebFetch to look at the live pages.

## Steps
1. **Triage.** For each failure, WebFetch the page to confirm it is real.
   - Some checks read server HTML only. A client-rendered `h1` may exist after JavaScript runs. If the rendered page clearly has it, it is not a real failure: note it and skip it.
2. **Site fixes.** Batch all real site failures into ONE `send_message` to the site project (`requestId: "{{run_id}}-qa-site"`). Be explicit, for example:
   - "Set the home `<title>` to '<55-char title>'";
   - "Add `<meta name=description>` with: '<150-char text>'";
   - "Generate an og:image (1200×630) in the brand colours";
   - "Add a canonical link";
   - "Ensure /robots.txt and /sitemap.xml are served".
   
   Write the actual copy from the site plan; don't ask the builder to invent it.
3. **App fixes.** For app reachability failures:
   - check `get_deployment_status` / `get_project` first: it may just be a cold start or still deploying;
   - send ONE fix message to the app project (`requestId: "{{run_id}}-qa-app"`) only if something is actually broken.
4. **Wait and republish.** Poll each build until completed. Republish the site if it was live, with the same 402 / PENDING_REVIEW rules as before (human_todos, never acknowledge).
5. **Re-check.** WebFetch again and sort each failure into `verified_fixed` or `still_failing`.

One round only. Do not loop.

## Output contract (`QAFixResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit qa_fix --file <file>` (SKILL.md has the loop).
