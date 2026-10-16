# Phase: embed_media — put the videos on the website

## Inputs
Site:
```json
{{site}}
```
Media (use only `public_urls`; local file paths are not reachable by the site):
```json
{{media}}
```
Brand:
```json
{{brand}}
```
Per-call cap `{{per_call_cap}}` · Run id `{{run_id}}`

## Tools (Greta MCP, server `greta`)
`send_message`, `get_generation_status`, `get_site_overview`, `publish_site`.

## Steps
1. Write ONE precise edit message for the site. Include only the parts whose URL exists in `public_urls`:
   - **Hero background (`hero_video`):** a full-bleed `<video>` behind the home hero with `autoplay muted loop playsinline preload="metadata"`, `poster` = `poster_image` if present, and `object-fit: cover`. Add a dark or brand-tinted overlay so the headline keeps AA contrast. On `prefers-reduced-motion: reduce`, show the poster instead of playing.
   - **"See it in action" section (`demo_video`)**, directly below the hero or the first feature block: a heading, one line of copy, and a `<video controls playsinline preload="none">` with the poster, a rounded frame and a brand-coloured shadow.
   - **Avatar explainer (`avatar_video`)**, if present: on the About page (or under the demo), with a short caption.
   - Keep everything else on the page unchanged. Do not touch other pages.
2. Call `send_message` with `requestId: "{{run_id}}-embed"`, `creditBudget` ≤ {{per_call_cap}}, `timeoutSeconds: 120`. Poll `get_generation_status` until completed. Answer any `waiting_for_answer` sensibly.
   - If it returns `completed_no_changes`, retry once with `requestId: "{{run_id}}-embed-r1"`, naming the exact component/file for the home hero.
3. If the site was already live (`site.published` true), call `publish_site` so the change ships. Handle 402 and PENDING_REVIEW exactly as in the site phase: record human_todos and never use acknowledge.
4. `embedded`: list which videos the builder actually confirmed adding, based on its changed files or summary.

## Output contract (`EmbedResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit embed_media --file <file>` (SKILL.md has the loop).
