# Phase: intake — turn the idea into a brief

## The idea, in the person's words
{{idea}}

Auto mode (no human available): {{auto_mode}}

Source kind: **{{source_kind}}** / source: **{{source_ref}}**  
(When source kind is not `idea`, a `recon` phase after this one will produce the full Teardown. Here, just frame the brief around rebuilding: set `source_kind`, `source_ref`, `rebuild_goal` (what to keep/change/improve) and `original_name_to_avoid`, and pick a fresh working name.)

## Your job
Produce a `Brief` that a researcher, a product designer and two builders can all work from without guessing.

## Steps
1. Read the idea and work out:
   - the product;
   - who it is for (specific segments, not "businesses");
   - the painful problem;
   - the 3–7 things a user must be able to DO (verb-first: "create an invoice", "send a payment reminder");
   - how it makes money;
   - the tone.
2. Decide what is genuinely open. A question is worth asking ONLY when the answer would change what gets built. Examples:
   - B2B vs consumer;
   - one-off vs subscription billing;
   - whether users need accounts at all;
   - which market or language.
   
   Do not ask about colours, names or wording: the blueprint phase handles those.
3. If auto mode is false and something important is open, call asking the user directly in the terminal ONCE with the single most important question and 2–4 concrete options. Otherwise decide yourself.
4. Record every decision you made without asking in `assumptions`, so the person can correct it at the review gate.
5. `wants_*` flags:
   - default all true;
   - set one false only if the person said they do not want it (e.g. "just the landing page" → `wants_app: false`);
   - an app with no accounts or data, a pure brochure, is `wants_app: false`.

## Revision feedback from the person (apply it if present)
{{feedback}}

Previous attempt: {{previous_output}}

## Output contract (`Brief`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit intake --file <file>` (SKILL.md has the loop).
