# Michael's Terminal Portfolio

A minimalist personal website with a terminal/CLI aesthetic. Type commands to explore!

**Live Site:** https://michaelguo.vercel.app

## Features

- **Interactive Terminal**: Type real commands to navigate
- **Tab Autocomplete**: Press Tab to autocomplete commands (Unix-style)
- **5 Color Themes**: Press `Shift+Tab` to cycle through themes
- **Commands**: `whoami`, `blog`, `portfolio`, `help`, `clear`, `home`
- **Blog Integration**: Links to Hugo blog at https://michaelguoblog.vercel.app
- **Responsive**: Works on desktop, tablet, and mobile
- **Lightweight**: Pure HTML, CSS, and vanilla JavaScript (no frameworks)

## Commands

| Command | Description |
|---------|-------------|
| `whoami` | About me and social links |
| `blog` | Opens my blog in new tab |
| `portfolio` | View my projects |
| `help` | Show all available commands |
| `clear` | Clear the terminal |
| `home` | Return to home page |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Autocomplete command |
| `Shift+Tab` | Cycle themes |
| `↑` / `↓` | Navigate command history |
| `Enter` | Execute command |

## Themes

Cycle through with `Shift+Tab`:
- **Classic** - Green on black
- **Amber** - Vintage monitor style
- **White** - High contrast
- **Dracula** - Modern dark theme
- **Matrix** - Green glow

## File Structure

```
/mywebsite
├── index.html          # Landing page
├── whoami.html         # Bio page
├── portfolio.html      # Projects page
├── styles.css          # Styling and themes
├── script.js           # Command system
├── README.md           # This file
└── AGENTS.md           # AI agent guide
```

## Local Development

```bash
# Start local server
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

## Deployment

Hosted on Vercel. Auto-deploys on push to main:

```bash
git add .
git commit -m "your changes"
git push
```

## Connected Blog

This portfolio links to a Hugo blog:
- **URL:** https://michaelguoblog.vercel.app
- **Tech:** Hugo + PaperMod theme
- **Repo:** https://github.com/michaelpersonal/michaels-blog

## Customization

### Add a Command

In `script.js`, add to the `commands` object:

```javascript
mycommand: {
    description: 'What it does',
    execute: () => {
        // Navigate to page
        window.location.href = 'mypage.html';
        return null;
        // Or open external link
        window.open('https://example.com', '_blank');
        return 'Opening...';
    }
}
```

### Add a Theme

In `styles.css`:

```css
body[data-theme="mytheme"] {
    --bg-color: #000000;
    --text-color: #00ff00;
    --prompt-color: #00ff00;
    --cursor-color: #00ff00;
    --header-bg: #1a1a1a;
    --link-color: #00cc00;
    --label-color: #00ff00;
}
```

Then add `'mytheme'` to the `themes` array in `script.js`.

## Social Links

- **GitHub:** https://github.com/michaelpersonal
- **X:** https://x.com/MichaelZSGuo
- **Blog:** https://michaelguoblog.vercel.app

## Credits

Inspired by [bentossell.com](https://www.bentossell.com/)

---

*There's no place like 127.0.0.1* 🏠

## Public top-post semantic search

The Vercel function `api/xposts-search.js` embeds queries on the server and ranks
the curated `xposts-embeddings.json` index. Configure these Vercel environment
variables before deploying:

- `EMBED_TOKEN`: bearer token for the embedding endpoint (server only).
- `X_EMBEDDING_BASE_URL`: optional; defaults to
  `https://michael-macbook-pro.tailf96f46.ts.net:8443/v1`.

The endpoint must be reachable from Vercel, such as through Tailscale Funnel.
Tailscale Serve alone permits only tailnet clients. The function uses the same
EmbeddingGemma 2 model, 768 dimensions and query prefix as the archive index.
Deploy the API, `vercel.json`, search script, page, and regenerated vector index
together. If the service is unavailable, the page labels the failure and switches
to keyword search. Tokens never go into browser JavaScript or static exports.
