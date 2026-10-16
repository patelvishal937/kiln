# Phase: email — onboarding sequence in Volanea

## Inputs
Brand:
```json
{{brand}}
```
Email plan:
```json
{{emails}}
```
URLs:
```json
{{urls}}
```

## Tools (Volanea MCP, server `volanea`)
Start with `volanea_get_project_status`, then `volanea_get_api_reference` for templates and workflows. Use `volanea_create_template`, `volanea_render_template`, `volanea_create_workflow`, `volanea_send_test_email`, `volanea_check_delivery`, `volanea_track_event`, `volanea_test_workflow`.

## Steps
1. **Check the project.** Read the project status. If no from-domain is verified, continue building, but add a human_todo: "Verify a sending domain in Volanea before emails go live".
2. **Templates.** Create one template per email in the plan:
   - subject;
   - preheader;
   - short body (≤150 words, one idea, one button);
   - the button links to `urls.app_preview_url` (or the site URL if the app has none);
   - brand primary colour on the button;
   - a plain-text alternative.
   
   Use personalisation variables (first name etc.) the way the API reference says, with a fallback. Render each template once to check it.
3. **Workflow.** Build ONE workflow:
   - trigger event `user_signed_up`;
   - each email after its `delay_hours`;
   - where the plan says "if the core action is not done", add a condition on an event such as `core_action_completed`.
   
   Workflows and campaigns stay as drafts or inactive unless the API only allows active workflows for test runs. Never send a campaign.
4. **Verify.**
   - `volanea_send_test_email` for the welcome template, then `volanea_check_delivery`;
   - `volanea_track_event` (`user_signed_up` for a test recipient), then `volanea_test_workflow` and read its run log.
   - Set `test_send_verified` true only if the delivery check confirms it.
5. **`integration_snippet`.** A short, copy-pasteable example of how the app's backend should fire `user_signed_up` and `core_action_completed` (HTTP call per the API reference, with the key read from an env var). Add a human_todo to wire it into the Greta app's signup handler.

## Output contract (`EmailResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit email --file <file>` (SKILL.md has the loop).
