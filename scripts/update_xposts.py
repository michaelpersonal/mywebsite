#!/usr/bin/env python3
"""
Regenerates xposts.html from xposts-data.json.

Legacy mode can still fetch recent X posts, but the preferred pipeline is now:
  x-content-os SQLite archive/sync -> export xposts-data.json -> render this page

Usage:
  python3 scripts/update_xposts.py --render-only

Legacy fetch mode requires X_BEARER_TOKEN env var.
"""

import os
import sys
import json
import re
import html as html_lib
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "xposts-data.json"
HTML_FILE = ROOT / "xposts.html"

TOKEN = os.environ.get("X_BEARER_TOKEN")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

SEARCH_RECENT_URL = "https://api.twitter.com/2/tweets/search/recent"
SEARCH_ALL_URL = "https://api.twitter.com/2/tweets/search/all"

# --- Configure these for your own use ---
USERNAME = "michaelzsguo"
MIN_IMPRESSIONS = 2000
SITE_TITLE = "X Posts"
BACK_LINK_URL = "index.html"
BACK_LINK_TEXT = "back to terminal"


def fetch_posts(backfill_days=None):
    """Fetch posts. If backfill_days is set, uses /search/all with a date range.
    Otherwise uses /search/recent (last 7 days)."""
    if not TOKEN:
        print("Error: X_BEARER_TOKEN env var not set")
        sys.exit(1)

    all_tweets = []
    next_token = None

    if backfill_days:
        base_url = SEARCH_ALL_URL
        start_time = (datetime.now(timezone.utc) - timedelta(days=backfill_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now(timezone.utc) - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        base_url = SEARCH_RECENT_URL
        start_time = None
        end_time = None

    while True:
        params = {
            "query": f"from:{USERNAME} -is:retweet -is:reply",
            "max_results": "100",
            "tweet.fields": "public_metrics,created_at,entities",
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if next_token:
            params["next_token"] = next_token

        url = base_url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            print(f"API error {e.code}: {e.read().decode()}")
            break

        if "data" in data:
            for tweet in data["data"]:
                if tweet["public_metrics"]["impression_count"] >= MIN_IMPRESSIONS:
                    all_tweets.append(tweet)

        page = len(all_tweets)
        if backfill_days:
            print(f"  ...{page} qualifying posts so far")

        if "meta" in data and "next_token" in data["meta"]:
            next_token = data["meta"]["next_token"]
            time.sleep(1)
        else:
            break

    return all_tweets


def clean_text(text):
    text = re.sub(r'https://t\.co/\w+', '', text)
    text = re.sub(r'^(@\w+\s*)+', '', text)
    return text.strip()


def get_existing_tags():
    """Get all tags already used in existing posts for consistency."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            posts = json.load(f)
        return sorted(set(t for p in posts for t in p.get("tags", [])))
    return []


def call_deepseek(prompt):
    """Call DeepSeek API and return the response text."""
    url = "https://api.deepseek.com/chat/completions"
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def generate_metadata_llm(tweets):
    """Use DeepSeek to generate title, summary, and tags for a batch of tweets."""
    existing_tags = get_existing_tags()
    tags_list = ", ".join(existing_tags) if existing_tags else "none yet"

    results = {}
    # Process in batches of 10
    for i in range(0, len(tweets), 10):
        batch = tweets[i:i+10]
        tweets_text = ""
        for j, tweet in enumerate(batch):
            text = tweet.get("article", {}).get("title", "") or tweet["text"]
            tweets_text += f"\n[{j}] {text}\n"

        prompt = f"""You are generating metadata for X/Twitter posts to display on a website.

Existing tags used so far: [{tags_list}]

For each post below, generate:
1. title: A short descriptive title (max 60 chars). If the post is in Chinese, title can be in Chinese.
2. summary: 1-2 sentence summary (max 200 chars)
3. tags: 1-4 tags. Reuse existing tags when they fit. Only create a new tag if the topic is genuinely new and not covered by existing tags.

Posts:
{tweets_text}

Respond in JSON array format, one object per post in order:
[{{"title": "...", "summary": "...", "tags": ["...", "..."]}}]

Return ONLY the JSON array, no other text."""

        try:
            response = call_deepseek(prompt)
            # Parse JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r'^```\w*\n?', '', response)
                response = re.sub(r'\n?```$', '', response)
            parsed = json.loads(response)
            for j, meta in enumerate(parsed):
                idx = i + j
                if idx < len(tweets):
                    results[tweets[idx]["id"]] = meta
        except Exception as e:
            print(f"  DeepSeek error on batch {i//10 + 1}: {e}")
            # Fall back to keyword-based for this batch
            for tweet in batch:
                results[tweet["id"]] = None

        if i + 10 < len(tweets):
            time.sleep(0.5)

    return results


def generate_tags_keyword(text):
    """Fallback keyword-based tag generation."""
    tags = []
    text_lower = text.lower()

    if any(k in text_lower for k in ['deepseek', 'ds4']):
        tags.append('DeepSeek')
    if any(k in text_lower for k in ['claude code', 'claude', 'anthropic', 'opus']):
        tags.append('Claude')
    if any(k in text_lower for k in ['codex', '/goal', 'goal-forge']):
        tags.append('Codex')
    if any(k in text_lower for k in ['openai', 'gpt', 'chatgpt']):
        tags.append('OpenAI')
    if any(k in text_lower for k in ['local llm', 'local model', 'ollama', 'llama.cpp', 'gguf', 'vram', 'tps', 'quantiz', 'mlx']):
        tags.append('Local LLM')
    if any(k in text_lower for k in ['gemma', 'google', 'gemini']):
        tags.append('Google')
    if any(k in text_lower for k in ['qwen']):
        tags.append('Qwen')
    if any(k in text_lower for k in ['mac', 'macbook', 'mac studio', 'm5', 'a100', 'gpu', 'hardware', 'raspberry pi']):
        tags.append('Hardware')
    if any(k in text_lower for k in ['harness', 'agent', 'hermes', 'openclaw']):
        tags.append('AI Agents')
    if any(k in text_lower for k in ['fine-tun', 'lora', 'training']):
        tags.append('Fine-tuning')
    if any(k in text_lower for k in ['skill', 'book']):
        tags.append('Skills')
    if any(k in text_lower for k in ['kv cache', 'context', 'memory', 'token']):
        tags.append('LLM Internals')
    if any(k in text_lower for k in ['security', 'attack', 'vulnerab', 'hack']):
        tags.append('Security')
    if any(k in text_lower for k in ['tailscale', 'tmux', 'remote', 'multiplayer']):
        tags.append('Remote Dev')
    if any(k in text_lower for k in ['cursor', 'fireworks']):
        tags.append('AI Tools')
    if any(k in text_lower for k in ['gbnf', 'grammar']):
        tags.append('Structured Output')
    if re.search(r'[一-鿿]', text):
        tags.append('中文')

    if not tags:
        tags.append('AI')

    return list(set(tags))[:4]


def generate_title_keyword(text):
    """Fallback keyword-based title generation."""
    text_clean = clean_text(text)
    first_sentence = re.split(r'[.。!！\n]', text_clean)[0].strip()
    if len(first_sentence) > 60:
        first_sentence = first_sentence[:57] + '...'
    if len(first_sentence) < 5:
        first_sentence = "Media Post"
    return first_sentence


def generate_summary_keyword(text):
    """Fallback keyword-based summary generation."""
    text_clean = clean_text(text)
    sentences = re.split(r'[.。!！\n]', text_clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    summary = '. '.join(sentences[:2])
    if len(summary) > 200:
        summary = summary[:197] + '...'
    return summary


def process_tweets(tweets):
    """Process tweets with LLM if available, otherwise fall back to keywords."""
    llm_metadata = {}
    if DEEPSEEK_API_KEY:
        print("Using DeepSeek for title/summary/tag generation...")
        llm_metadata = generate_metadata_llm(tweets)
    else:
        print("No DEEPSEEK_API_KEY set, using keyword-based tagging (set it for better results)")

    results = []
    for tweet in tweets:
        pm = tweet["public_metrics"]
        article_title = tweet.get("article", {}).get("title", "")
        meta = llm_metadata.get(tweet["id"])

        if meta:
            title = meta.get("title", "") or article_title or generate_title_keyword(tweet["text"])
            summary = meta.get("summary", "") or generate_summary_keyword(tweet["text"])
            tags = meta.get("tags", []) or generate_tags_keyword(tweet["text"])
        else:
            title = article_title if article_title else generate_title_keyword(tweet["text"])
            summary = article_title if (article_title and not clean_text(tweet["text"])) else generate_summary_keyword(tweet["text"])
            tags = generate_tags_keyword(tweet["text"])

        results.append({
            "id": tweet["id"],
            "title": title,
            "summary": summary,
            "tags": tags[:4],
            "impressions": pm["impression_count"],
            "likes": pm["like_count"],
            "retweets": pm["retweet_count"],
            "bookmarks": pm["bookmark_count"],
            "date": tweet["created_at"][:10],
            "url": f"https://x.com/{USERNAME}/status/{tweet['id']}"
        })

    return results


def merge_posts(existing, new_posts):
    existing_ids = {p["id"] for p in existing}
    added = 0
    for post in new_posts:
        if post["id"] not in existing_ids:
            existing.append(post)
            added += 1
    existing.sort(key=lambda p: p["impressions"], reverse=True)
    return existing, added


def fmt_num(n):
    n = int(n or 0)
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def build_html(posts):
    all_tags = sorted(set(t for p in posts for t in p["tags"]))

    cards_html = ""
    for p in posts:
        tags = p.get("tags", [])
        tags_html = " ".join(f'<span class="tag">{html_lib.escape(str(t))}</span>' for t in tags)
        data_tags = html_lib.escape(" ".join(str(t) for t in tags).lower(), quote=True)
        url = html_lib.escape(str(p.get("url", "")), quote=True)
        title = html_lib.escape(str(p.get("title", "")))
        date = html_lib.escape(str(p.get("date", "")))
        summary = html_lib.escape(str(p.get("summary", "")))
        impressions = int(p.get("impressions") or 0)
        likes = int(p.get("likes") or 0)
        bookmarks = int(p.get("bookmarks") or 0)
        cards_html += f'''    <a href="{url}" target="_blank" class="post-card" data-tags="{data_tags}" data-impressions="{impressions}">
      <div class="post-header">
        <h3 class="post-title">{title}</h3>
        <span class="post-date">{date}</span>
      </div>
      <p class="post-summary">{summary}</p>
      <div class="post-footer">
        <div class="post-tags">{tags_html}</div>
        <div class="post-stats">
          <span class="stat">{fmt_num(impressions)} views</span>
          <span class="stat">{fmt_num(likes)} likes</span>
          <span class="stat">{fmt_num(bookmarks)} saves</span>
        </div>
      </div>
    </a>
'''

    filter_buttons = '<button class="filter-btn active" data-filter="all">All</button>\n'
    for tag in all_tags:
        filter_buttons += f'      <button class="filter-btn" data-filter="{html_lib.escape(str(tag).lower(), quote=True)}">{html_lib.escape(str(tag))}</button>\n'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_TITLE} - @{USERNAME}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem 1rem;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #222; }}
        h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; color: #fff; }}
        .subtitle {{ color: #888; font-size: 0.9rem; }}
        .subtitle a {{ color: #1d9bf0; text-decoration: none; }}
        .back-link {{ display: inline-block; margin-bottom: 1rem; color: #1d9bf0; text-decoration: none; font-size: 0.85rem; }}
        .back-link:hover {{ text-decoration: underline; }}
        .controls {{ display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }}
        .search-box {{
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1px solid #333;
            border-radius: 8px;
            background: #111;
            color: #e0e0e0;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{ border-color: #1d9bf0; }}
        .search-box::placeholder {{ color: #555; }}
        .filters {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .filter-btn {{
            padding: 0.4rem 0.8rem;
            border: 1px solid #333;
            border-radius: 20px;
            background: transparent;
            color: #aaa;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn:hover {{ border-color: #1d9bf0; color: #1d9bf0; }}
        .filter-btn.active {{ background: #1d9bf0; border-color: #1d9bf0; color: #fff; }}
        .results-count {{ font-size: 0.85rem; color: #666; margin-bottom: 1rem; }}
        .posts-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .post-card {{
            display: block;
            padding: 1.25rem;
            border: 1px solid #1a1a1a;
            border-radius: 10px;
            background: #111;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s;
        }}
        .post-card:hover {{ border-color: #333; background: #161616; transform: translateY(-1px); }}
        .post-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 0.5rem; }}
        .post-title {{ font-size: 1rem; font-weight: 600; color: #fff; line-height: 1.4; }}
        .post-date {{ font-size: 0.75rem; color: #666; white-space: nowrap; flex-shrink: 0; }}
        .post-summary {{ font-size: 0.85rem; color: #999; line-height: 1.5; margin-bottom: 0.75rem; }}
        .post-footer {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; }}
        .post-tags {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
        .tag {{ padding: 0.2rem 0.5rem; border-radius: 4px; background: #1a2a3a; color: #5ba3d9; font-size: 0.7rem; font-weight: 500; }}
        .post-stats {{ display: flex; gap: 0.75rem; }}
        .stat {{ font-size: 0.75rem; color: #555; }}
        .no-results {{ text-align: center; padding: 3rem; color: #555; }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem 0.75rem; }}
            .post-header {{ flex-direction: column; gap: 0.25rem; }}
            .post-footer {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="{BACK_LINK_URL}" class="back-link">&larr; {BACK_LINK_TEXT}</a>
        <header>
            <h1>{SITE_TITLE}</h1>
            <p class="subtitle">Curated archive-backed posts by <a href="https://x.com/{USERNAME}" target="_blank">@{USERNAME}</a> &mdash; {len(posts)} searchable posts</p>
        </header>
        <div class="controls">
            <input type="text" class="search-box" placeholder="Search posts... (e.g. DeepSeek, local LLM, harness)" id="search">
            <div class="filters">
                {filter_buttons}
            </div>
        </div>
        <div class="results-count" id="results-count">{len(posts)} posts</div>
        <div class="posts-list" id="posts-list">
{cards_html}
        </div>
        <div class="no-results" id="no-results" style="display:none">
            No posts match your search.
        </div>
    </div>
    <script>
        const searchInput = document.getElementById('search');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const posts = Array.from(document.querySelectorAll('.post-card'));
        const resultsCount = document.getElementById('results-count');
        const noResults = document.getElementById('no-results');

        let activeFilter = 'all';

        const postSearchData = posts.map(post => ({{
            el: post,
            text: (post.textContent + ' ' + (post.dataset.tags || '')).replace(/\\s+/g, ' ').toLowerCase(),
            tags: post.dataset.tags || ''
        }}));

        function filterPosts() {{
            const query = searchInput.value.toLowerCase().trim();
            let visible = 0;

            postSearchData.forEach(({{ el, text, tags }}) => {{
                const matchesSearch = !query || text.includes(query);
                const matchesFilter = activeFilter === 'all' || tags.includes(activeFilter);

                if (matchesSearch && matchesFilter) {{
                    el.style.display = 'block';
                    visible++;
                }} else {{
                    el.style.display = 'none';
                }}
            }});

            resultsCount.textContent = visible + ' post' + (visible !== 1 ? 's' : '');
            noResults.style.display = visible === 0 ? 'block' : 'none';
        }}

        searchInput.addEventListener('input', filterPosts);
        searchInput.addEventListener('keyup', filterPosts);

        filterBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                activeFilter = btn.dataset.filter;
                filterPosts();
            }});
        }});
    </script>
</body>
</html>'''
    return html


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Update X posts page")
    parser.add_argument("--render-only", action="store_true",
                        help="Only regenerate xposts.html from xposts-data.json. Does not call X.")
    parser.add_argument("--backfill", type=int, metavar="DAYS",
                        help="Initial backfill: fetch posts from the last N days (uses /search/all, requires Academic/Pro tier)")
    args = parser.parse_args()

    # Load existing data
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            existing = json.load(f)
    else:
        existing = []

    print(f"Existing posts: {len(existing)}")

    if args.render_only:
        html_out = build_html(existing)
        with open(HTML_FILE, "w") as f:
            f.write(html_out)
        print(f"Regenerated {HTML_FILE.name}")
        return

    # Fetch posts
    if args.backfill:
        print(f"Backfilling last {args.backfill} days (using /search/all)...")
        raw_tweets = fetch_posts(backfill_days=args.backfill)
        print(f"Found {len(raw_tweets)} posts with {MIN_IMPRESSIONS}+ impressions")
    else:
        print("Fetching recent posts (last 7 days)...")
        raw_tweets = fetch_posts()
        print(f"Found {len(raw_tweets)} posts with {MIN_IMPRESSIONS}+ impressions in last 7 days")

    # Process and merge
    new_posts = process_tweets(raw_tweets)
    merged, added = merge_posts(existing, new_posts)
    print(f"Added {added} new posts (total: {len(merged)})")

    # Save data
    with open(DATA_FILE, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    # Rebuild HTML
    html = build_html(merged)
    with open(HTML_FILE, "w") as f:
        f.write(html)

    print(f"Regenerated {HTML_FILE.name}")


if __name__ == "__main__":
    main()
