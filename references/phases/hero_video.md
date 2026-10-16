# Phase: hero_video — homepage background loop (Higgsfield)

## Inputs
Brand:
```json
{{brand}}
```
Video plan:
```json
{{video_plan}}
```

## Your job
Make ONE seamless, muted 6–10 second background loop for the homepage hero, plus a poster image. A background video sits BEHIND headline text, so it must:
- be calm, with slow camera motion, no hard cuts and no flashing;
- have nothing readable in it: no text, no logos, no UI;
- have no recognisable faces;
- have mid-to-low contrast, so white or dark headline text stays readable on top;
- use the brand palette (hex colours above) as the dominant tones;
- be 16:9, at least 1080p if offered.

## Steps
1. Read the server's instructions/tools first. If it offers workflow or preset instructions for multi-step video, read them before generating.
2. Generate a key frame image from `hero_loop_prompt` (adapted to the rules above), then animate it into video. If the server offers direct text-to-video with good quality, one step is fine.
3. Wait for the job to finish with the server's wait/status tool. Get the final hosted URL from the result. Never construct a URL.
4. If the first result breaks a rule (text, faces, jarring motion), you may regenerate once with a corrected prompt. Kiln caps generations at 4 per run.
5. `poster_url`: the key frame image URL if you made one.

## Rules
- Do not publish anywhere, change account settings or buy anything.
- If generation fails, submit `video_url: "FAILED"` and explain why in `notes`. The engine then falls back to the Remotion hero loop.

## Output contract (`HeroVideoResult`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit hero_video --file <file>` (SKILL.md has the loop).
