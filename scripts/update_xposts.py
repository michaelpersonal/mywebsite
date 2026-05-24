#!/usr/bin/env python3
"""
Fetches recent X posts (last 7 days) with 2000+ impressions,
merges them into xposts-data.json, and regenerates xposts.html.

Usage:
  python3 scripts/update_xposts.py

Requires X_BEARER_TOKEN env var.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "xposts-data.json"
HTML_FILE = ROOT / "xposts.html"

TOKEN = os.environ.get("X_BEARER_TOKEN")
if not TOKEN:
    print("Error: X_BEARER_TOKEN env var not set")
    sys.exit(1)

SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
USERNAME = "michaelzsguo"
MIN_IMPRESSIONS = 2000


def fetch_recent_posts():
    all_tweets = []
    next_token = None

    while True:
        params = {
            "query": f"from:{USERNAME} -is:retweet",
            "max_results": "100",
            "tweet.fields": "public_metrics,created_at,entities",
        }
        if next_token:
            params["next_token"] = next_token

        url = SEARCH_URL + "?" + urllib.parse.urlencode(params)
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


def generate_tags(text):
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


def generate_title(text):
    text_clean = clean_text(text)
    first_sentence = re.split(r'[.。!！\n]', text_clean)[0].strip()
    if len(first_sentence) > 60:
        first_sentence = first_sentence[:57] + '...'
    if len(first_sentence) < 5:
        first_sentence = "Media Post"
    return first_sentence


def generate_summary(text):
    text_clean = clean_text(text)
    sentences = re.split(r'[.。!！\n]', text_clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    summary = '. '.join(sentences[:2])
    if len(summary) > 200:
        summary = summary[:197] + '...'
    return summary


def process_tweet(tweet):
    pm = tweet["public_metrics"]
    return {
        "id": tweet["id"],
        "title": generate_title(tweet["text"]),
        "summary": generate_summary(tweet["text"]),
        "tags": generate_tags(tweet["text"]),
        "impressions": pm["impression_count"],
        "likes": pm["like_count"],
        "retweets": pm["retweet_count"],
        "bookmarks": pm["bookmark_count"],
        "date": tweet["created_at"][:10],
        "url": f"https://x.com/{USERNAME}/status/{tweet['id']}"
    }


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
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def build_html(posts):
    all_tags = sorted(set(t for p in posts for t in p["tags"]))

    cards_html = ""
    for p in posts:
        tags_html = " ".join(f'<span class="tag">{t}</span>' for t in p["tags"])
        data_tags = " ".join(p["tags"]).lower()
        cards_html += f'''    <a href="{p['url']}" target="_blank" class="post-card" data-tags="{data_tags}" data-impressions="{p['impressions']}">
      <div class="post-header">
        <h3 class="post-title">{p['title']}</h3>
        <span class="post-date">{p['date']}</span>
      </div>
      <p class="post-summary">{p['summary']}</p>
      <div class="post-footer">
        <div class="post-tags">{tags_html}</div>
        <div class="post-stats">
          <span class="stat">{fmt_num(p['impressions'])} views</span>
          <span class="stat">{fmt_num(p['likes'])} likes</span>
          <span class="stat">{fmt_num(p['bookmarks'])} saves</span>
        </div>
      </div>
    </a>
'''

    filter_buttons = '<button class="filter-btn active" data-filter="all">All</button>\n'
    for tag in all_tags:
        filter_buttons += f'      <button class="filter-btn" data-filter="{tag.lower()}">{tag}</button>\n'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>X Posts - Michael Guo (@michaelzsguo)</title>
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
        <a href="index.html" class="back-link">&larr; back to terminal</a>
        <header>
            <h1>X Posts</h1>
            <p class="subtitle">Top posts by <a href="https://x.com/{USERNAME}" target="_blank">@{USERNAME}</a> &mdash; {len(posts)} posts with 2,000+ impressions</p>
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
    # Load existing data
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            existing = json.load(f)
    else:
        existing = []

    print(f"Existing posts: {len(existing)}")

    # Fetch new posts from last 7 days
    print("Fetching recent posts...")
    raw_tweets = fetch_recent_posts()
    print(f"Found {len(raw_tweets)} posts with {MIN_IMPRESSIONS}+ impressions in last 7 days")

    # Process and merge
    new_posts = [process_tweet(t) for t in raw_tweets]
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
