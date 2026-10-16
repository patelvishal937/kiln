# Phase: recon — reverse-engineer the existing product into a Teardown

## Inputs
```json
{{brief}}
```
Source kind: **{{source_kind}}** · Source: **{{source_ref}}**

## What this is
The user wants to rebuild an existing product. Your job is to map HOW that product is
put together — its jobs, screens, flows, data and tech — into a structured `Teardown`
that the blueprint phase turns into an ORIGINAL, re-branded product on Greta.

You are mapping structure, not copying a product. Record ideas, architecture and small
samples. Put every trademark, logo, brand name and block of verbatim copy into
`do_not_copy` — the rebuild recreates those from scratch under a new name.

---

## If source_kind is `website`

1. **Mechanical pass.** Run the analyzer:
   ```
   kiln recon-site {{source_ref}}
   ```
   It writes `recon.json` into the run's assets and prints the nav, tech signals and
   whether a sitemap exists. Read `recon.json` — it has per-page titles, headings,
   forms, JSON-LD types, internal links and a colour/font sample.
2. **Eyes on the product.** Open the site in the browser pane (preview_start / navigate),
   look at the 4–8 most important pages, and screenshot the homepage and one core
   screen into the run's assets. The analyzer sees structure; you see the experience.
3. **Synthesize the Teardown:**
   - `primary_jobs`: what someone hires this product to do.
   - `information_architecture`: one node per real page/section (locator = its path).
   - `key_screens`: the notable pages, each with the UI building blocks it uses
     (hero, pricing table, dashboard, form…) — components, not pixels.
   - `core_flows`: the 2–4 journeys that matter (e.g. browse → sign up → onboard → first action).
   - `data_entities`: the records the product clearly stores, inferred from forms,
     listings and JSON-LD (e.g. `listing: title, price, location, photos`).
   - `tech_signals`: from `recon.json` (Next.js, Shopify, etc.).
   - `design_language`: colours (hex) and fonts from the sample — as REFERENCE for an
     original palette, not to copy exactly.
   - `content_model`: recurring content types (blog post, product, case study…).
   - `strengths` / `gaps`: what it does well, and where the rebuild can be better.
   - `rebuild_notes`: how to build an original equivalent on Greta (which kind —
     full_stack app vs self_growing site — and the key moves).

## If source_kind is `apk`

1. Use the installed **`apk-reverse`** skill as the extraction engine — it is the right
   tool for unpacking and mapping an Android app. If it is not installed, stop and add a
   human_todo: "Install the apk-reverse skill: `npx skills add newliver666/apk-reverse --skill apk-reverse -y`", then submit what you can.
2. Drive it only to understand the app at the level this Teardown needs — screens,
   navigation, the features and screens the user wants rebuilt, obvious data entities,
   and backend/integration endpoints it talks to. You are producing a feature map to
   rebuild an original app, not modifying or repackaging the original binary.
3. Fill the same Teardown fields from what you learn. `tech_signals` = the app's stack
   (native, Flutter, React Native, WebView…). `integrations_detected` = the APIs/SDKs it
   calls. Everything branded goes in `do_not_copy`.

---

## Rules
- Respect access: only analyze a product the user is entitled to study. If the site
  blocks automated access or the APK is DRM/anti-tamper protected beyond read-level
  inspection, record that in `confidence_notes` and `gaps` and work from what is visible.
- Never put proprietary brand names, logos or verbatim marketing copy into any field
  except `do_not_copy`.
- `confidence_notes`: say what you could not see and what is inferred.

## Output contract (`Teardown`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit recon --file <file>` (SKILL.md has the loop).
