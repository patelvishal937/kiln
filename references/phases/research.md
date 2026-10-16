# Phase: research — evidence for every later decision

## Brief
```json
{{brief}}
```

Apify available: **{{apify_available}}**

Teardown of the product being rebuilt (or "(none)" for a fresh idea):
```json
{{teardown}}
```

## Your job
Find out:
- who already serves these customers;
- what customers complain about;
- what people search for;
- what this product must have to compete.

Every claim needs a source URL. The blueprint phase turns this into the product, the site and a 12-week SEO calendar, so the keyword ideas are the most important output.

## Steps
1. **Competitors (4–8).** Start from `known_competitors`, then search "<category> software", "<category> alternatives" and "best <category> for <segment>". For each competitor, fetch the homepage and pricing page and record: positioning in one line, pricing tiers, strengths, weaknesses.
2. **Customer pains (5–10).** Look where real users talk: Reddit threads, G2/Capterra reviews, app store reviews, forums. Paraphrase each pain and cite its URL. Prefer pains that repeat across sources.
3. **Keyword ideas (15–30).** Mix intents:
   - commercial: "best X for Y", "X vs Y", "X alternatives";
   - informational: "how to …", "what is …", "… template";
   - transactional: "X software", "X app free".
   
   Favour long-tail, winnable queries over head terms. Estimate difficulty 0–100 if you have no tool data, and say it is an estimate in `why`.
4. **Must-have features**: what every serious competitor has. **Differentiation angles (2–4)**: gaps where the pains are loud and competitors are weak.
5. `pricing_benchmarks`: one line per competitor tier that matters.

## Tools
- **If Apify is available:**
  - use `search-actors` to find the right Actor (Google Search results scraper, Reddit scraper, G2/Capterra review scraper, website content crawler);
  - check its input schema with `fetch-actor-details`;
  - run it with `call-actor`, keeping inputs small (≤20 results per query, ≤3 queries per Actor);
  - read the output with `get-dataset-items`;
  - spend at most ~8 Actor runs.
  
  Set `used_apify: true` if you used it.
- **Always available:** WebSearch and WebFetch. They are enough on their own, so use them for gaps or when Apify fails.
- Stop when you have enough to decide. Do not crawl for the sake of it. Aim for ≤40 tool calls.

## Rules
- Never invent a competitor, price, quote or statistic. If you could not verify it, leave it out or mark it "unverified".
- `confidence_notes`: one paragraph on what is thin, e.g. "no review data for segment X".

## Output contract (`Research`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit research --file <file>` (SKILL.md has the loop).
