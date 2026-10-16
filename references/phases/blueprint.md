# Phase: blueprint — the single source of truth

## Brief
```json
{{brief}}
```

## Research
```json
{{research}}
```

## Teardown (present only when rebuilding an existing product; "(none)" otherwise)
```json
{{teardown}}
```
When a Teardown is present, base the app `data_models`, `pages` and `build_milestones` on its `data_entities`, `information_architecture` and `core_flows`, and the site on its IA — but the brand, name, copy and visuals are ORIGINAL (honour `do_not_copy`). Beat the `gaps` it lists.

## Your job
Write the **Blueprint** that every builder works from:
- the app builder (Greta full-stack);
- the site builder (Greta self-growing);
- the video renderer;
- the email writer.

When this is right, everything downstream is consistent and specific. When it is vague, every output becomes generic. The person reviews this before any credits are spent.

## Section by section

### brand
- `name`: keep the working name if it is good. Otherwise pick a short, pronounceable name that does not collide with the competitors.
- `tagline`: ≤8 words, and it states the outcome.
- `colors`: hex values with a real palette logic: one confident primary, a supporting secondary, one accent used sparingly, and background + text with WCAG AA contrast. Avoid the default "indigo-500 on white" look.
- Fonts: Google Fonts names (e.g. "Space Grotesk" / "Inter"). `logo_concept`: one sentence.

### positioning, pricing
- Positioning: one sentence, `For <segment> who <pain>, <name> is the <category> that <differentiator>, unlike <competitor>.`
- Pricing: concrete tiers informed by `pricing_benchmarks`.

### app (Greta full-stack builder)
- `data_models`: name + fields with types (`invoice: id, client_id→client, amount:number, currency, status:enum(draft|sent|paid|overdue), due_date:date`).
- `pages`: every route with a purpose. Include auth pages, the main dashboard, the core CRUD flows and settings.
- `build_milestones`: 3–5 messages. Each one is a complete, standalone instruction to the builder, because the builder only sees one message at a time. Order:
  1. Foundation: stack defaults, auth, data models, seed data, app shell + navigation with brand colours/fonts.
  2. The core workflow end to end (the one thing users come for).
  3. Secondary features + settings + empty/loading/error states.
  4. (if paid) Pricing/plan limits UI. (Optional) Polish: responsive pass, onboarding checklist, demo data.
  
  Each milestone names the routes, fields, buttons and acceptance behaviour. 120–350 words each.
- `acceptance_checks`: 4–8 click-through checks ("sign up → create client → create invoice → status shows Draft").

### site (Greta self-growing builder)
- `pages`: home, features (or one page per key feature), pricing, about, contact, privacy, terms; add one comparison page if research found a dominant competitor. List `key_sections` for each.
- `primary_cta`: the action, with its target. Use the literal text `{APP_URL}` where the app link goes; the site phase substitutes it.
- `build_prompt`: the full first-turn prompt for the site builder, 250–500 words. It must answer, up front, everything a builder would otherwise stop and ask:
  - the pages and their sections;
  - who it is for;
  - the offer and pricing;
  - lead capture via Greta Forms;
  - the CTA target `{APP_URL}`;
  - the brand colours and fonts;
  - the tone;
  - and that the home hero must leave room for a background video.
  
  Write it the way a sharp founder would brief a designer.

### seo_calendar (12 weeks)
- 8–16 tasks drawn from `keyword_ideas`, roughly 1–2 per week. Put commercial and comparison pages first (they convert), then informational guides that build topical authority around the core keyword cluster.
- Each `brief` (20–1500 chars) states: who the reader is, what they need, the angle that beats the current top results, and the internal link to the product (CTA to `{APP_URL}`).
- Do not duplicate pages already in `site.pages`.

### video
- `demo_scenes` (3–7): each one is a screen the viewer sees.
  - `screen: "app"` with a real app route from `app.pages`, or `screen: "site"`.
  - Title ≤40 chars, caption ≤110 chars, written as benefits ("Chase late payments automatically").
- `hook_line` ≤60 chars: the first thing on screen. Make it a pain or a bold promise.
- `cta_line` ≤50 chars.
- `hero_loop_prompt`: a text-to-video prompt for an 6–10s seamless, muted, abstract-but-on-brand background loop. Describe subject, camera move, palette (use the hex colours) and mood. No text, no logos, no people's faces.
- `avatar_script`: 45–75 seconds spoken. Hook → problem → product → 3 benefits → CTA. Plain spoken English, no stage directions.

### emails
3–6 onboarding emails:
- welcome (immediate);
- activation nudge if the core action is not done (24h);
- feature tip (72h);
- social proof / case story (day 5);
- upgrade (day 7, only if paid).

Each email has a clear single goal.

### launch_channels
Where these customers actually are (from research), e.g. specific subreddits, communities, Product Hunt, LinkedIn groups.

## Revision feedback from the person (apply it if present)
{{feedback}}

Previous attempt: {{previous_output}}

## Output contract (`Blueprint`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit blueprint --file <file>` (SKILL.md has the loop). No tools other than submit are needed in this phase.
