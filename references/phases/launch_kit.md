# Phase: launch_kit — launch copy for the channels

## Inputs
Brief:
```json
{{brief}}
```
Blueprint:
```json
{{blueprint}}
```
Research:
```json
{{research}}
```
Live URLs:
```json
{{urls}}
```

## Your job
Write ready-to-post launch copy in the brand voice. Use the real URLs where a link belongs: the site for discovery posts, the app for direct sign-up. If a URL is empty, write `[link]`.

- **Product Hunt:**
  - tagline ≤60 chars;
  - description ≤260 chars;
  - maker's first comment: why we built it, who it is for, what is next, and a question for the community.
- **X thread (5–8 posts):**
  - post 1 is the hook (a pain from research, stated sharply);
  - one benefit per post with a concrete example;
  - the last post is the CTA with the link;
  - no hashtag spam; at most one emoji per post.
- **LinkedIn post:** a founder voice, a short story about the problem, 3 bullet benefits, the CTA.
- **Reddit angles (2–4):** for the subreddits in `launch_channels`. Each one is value-first ("here's how we solved X"). Name the subreddit, title and the gist, and follow self-promo norms.
- **Cold email:** ≤120 words to one target segment, with one specific pain, one proof point and one low-friction ask.
- **Short-video captions (3+):** for the 9:16 demo cut.

No invented metrics, customers or testimonials.

## Output contract (`LaunchKit`)
```json
{{output_schema}}
```
Save your result as a JSON object matching the contract and submit it: write it to a file and run `kiln submit launch_kit --file <file>` (SKILL.md has the loop).
