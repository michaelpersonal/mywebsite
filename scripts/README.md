# X Posts Render Script

Renders `xposts.html` from `xposts-data.json`.

The source of truth for X ingestion now lives in:

```text
/Users/zhisongguo/code/x-content-os
```

That system imports Michael's official X archive into SQLite, incrementally syncs new authored posts, exports a curated public subset to this repo, and then calls this renderer.

## What it does

1. Reads `xposts-data.json`
2. Regenerates `xposts.html`
3. Produces a searchable, filterable static page with tags and engagement metadata

Legacy X API fetch mode still exists in `scripts/update_xposts.py`, but it should not be used as the scheduled ingestion path.

## Setup

### Prerequisites

- Python 3.10+
- `xposts-data.json`, exported by `x-content-os`

### Run locally

```bash
python3 scripts/update_xposts.py --render-only
```

From `x-content-os`, run the full local publishing path:

```bash
cd /Users/zhisongguo/code/x-content-os
python3 scripts/x_posts.py publish-website --website-root /Users/zhisongguo/code/mywebsite
```

Or run the scheduled wrapper:

```bash
cd /Users/zhisongguo/code/x-content-os
scripts/publish_xposts_website.sh
```

### GitHub Actions

The included workflow is manual-only and renders the page from committed `xposts-data.json`.
It does not fetch from X.

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
x-content-os SQLite archive/sync store
  → export curated public posts to xposts-data.json
  → regenerate xposts.html
  → commit & push static artifacts
```

## Files

| File | Purpose |
|------|---------|
| `scripts/update_xposts.py` | Static page renderer; legacy fetch mode remains for manual fallback |
| `xposts-data.json` | Source of truth for all posts |
| `xposts.html` | Generated static page |
| `.github/workflows/update-xposts.yml` | Manual render workflow |

## Limitations

- `xposts.html` is generated. Edit `scripts/update_xposts.py` or `xposts-data.json`, not the generated card markup by hand.
- Public metrics are only as complete as the upstream archive/API data and preserved `xposts-data.json` history.
- Tag generation is keyword-based for newly exported archive posts unless curated metadata already exists.
