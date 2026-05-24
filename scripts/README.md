# X Posts Update Script

Fetches your top-performing X (Twitter) posts and publishes them as a searchable, filterable static page.

## What it does

1. Fetches posts from the last 7 days using the X API (`/search/recent`)
2. Filters for posts with 2,000+ impressions
3. Auto-generates titles, summaries, and topic tags
4. Merges new posts into `xposts-data.json` (deduplicates by tweet ID)
5. Regenerates `xposts.html` — a static page with search and tag filtering

## Setup

### Prerequisites

- Python 3.10+
- An X API Bearer Token (Basic tier or higher — needs access to `impression_count` in `public_metrics`)
- (Optional) A DeepSeek API key — for LLM-powered title/summary/tag generation. Without it, falls back to keyword matching.

### Get your X API token

1. Go to https://developer.x.com/en/portal/dashboard
2. Create a project/app if you don't have one
3. Generate a Bearer Token (app-only authentication)

### Run locally

```bash
export X_BEARER_TOKEN="your-bearer-token"
export DEEPSEEK_API_KEY="your-deepseek-key"  # optional, for better tagging

# Weekly update (last 7 days, default)
python3 scripts/update_xposts.py

# Initial backfill (e.g. last 90 days — requires /search/all access)
python3 scripts/update_xposts.py --backfill 90
```

The `--backfill` flag uses the full-archive search endpoint to fetch historical posts. Use this on first setup to populate your page. After that, the default weekly mode keeps it current.

### Automate with GitHub Actions

The included workflow (`.github/workflows/update-xposts.yml`) runs every Monday at 9am UTC.

To set it up:

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add a secret named `X_BEARER_TOKEN` with your bearer token
3. (Optional) Add a secret named `DEEPSEEK_API_KEY` for LLM-powered metadata generation

You can also trigger it manually from the Actions tab → "Update X Posts" → "Run workflow".

## Configuration

Edit these variables at the top of `update_xposts.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `USERNAME` | `michaelzsguo` | X handle to fetch posts from |
| `MIN_IMPRESSIONS` | `2000` | Minimum impressions threshold |
| `SITE_TITLE` | `X Posts` | Page heading |
| `BACK_LINK_URL` | `index.html` | "Back" link destination (or remove if standalone) |
| `BACK_LINK_TEXT` | `back to terminal` | "Back" link label |

### Tags

When `DEEPSEEK_API_KEY` is set, the script uses DeepSeek to generate titles, summaries, and tags. It passes the existing tag list as context so new posts stay consistent with existing categories, and only introduces new tags when the topic is genuinely new.

Without the API key, it falls back to keyword matching. You can add new keyword rules in `generate_tags_keyword()`.

## How it works

```
X API (/search/recent, 7-day window)
  → filter by impressions >= 2000
  → generate title/summary/tags
  → deduplicate against xposts-data.json
  → merge and sort by impressions (descending)
  → regenerate xposts.html
  → commit & push (in GitHub Actions)
```

## Files

| File | Purpose |
|------|---------|
| `scripts/update_xposts.py` | The update script |
| `xposts-data.json` | Source of truth for all posts |
| `xposts.html` | Generated static page |
| `.github/workflows/update-xposts.yml` | Weekly automation |

## Adapting for your own use

1. Fork this repo
2. Change `USERNAME` in the script to your X handle
3. Update `SITE_TITLE`, `BACK_LINK_URL`, and `BACK_LINK_TEXT` for your site
4. Adjust `MIN_IMPRESSIONS` to your threshold
5. Delete `xposts-data.json` (that's my data, you want a fresh start)
6. Run the initial backfill to generate your page:
   ```bash
   export X_BEARER_TOKEN="your-bearer-token"
   export DEEPSEEK_API_KEY="your-deepseek-key"  # optional
   python3 scripts/update_xposts.py --backfill 90
   ```
   This fetches your posts from the last 90 days (adjust as needed), generates titles/summaries/tags, and creates both `xposts-data.json` and `xposts.html`.
7. Add `X_BEARER_TOKEN` (and optionally `DEEPSEEK_API_KEY`) as GitHub repo secrets
8. Push — the action will start running weekly to pick up new posts

## Limitations

- `/search/recent` only covers the last 7 days. If two consecutive runs fail, posts from the gap period are lost.
- X API credits can deplete. The Basic tier has monthly limits.
- Article-only posts (no text body) get their title from the API's `article.title` field. Image/video-only posts without articles fall back to "Media Post".
- Tag generation is keyword-based and may not cover new topics. Update `generate_tags()` as needed.
