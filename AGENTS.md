# AGENTS.md - Project Maintenance Guide

This document provides context for AI agents and developers working on Michael's terminal-style portfolio website.

## Project Overview

A minimalist personal portfolio website with an interactive terminal/CLI aesthetic, inspired by bentossell.com. Built with pure HTML, CSS, and vanilla JavaScript (no frameworks).

**Live Sites:**
- **Portfolio:** https://michaelguo.vercel.app
- **Blog:** https://michaelguoblog.vercel.app

**Repositories:**
- **Portfolio:** https://github.com/michaelpersonal/mywebsite
- **Blog:** https://github.com/michaelpersonal/michaels-blog

## Core Features

1. **Interactive Terminal Interface**: Real command-line input where users can type commands
2. **Command System**: Navigate between pages using terminal commands (`whoami`, `blog`, `portfolio`, `help`, `clear`, `home`)
3. **Tab Autocomplete**: Press Tab to autocomplete commands (Unix-style), cycles through matches
4. **Theme Switcher**: 5 color themes (classic, amber, white, dracula, matrix) - cycle with `Shift+Tab`
5. **Command History**: Navigate previous commands with up/down arrow keys
6. **Dynamic Input Sizing**: Input field expands as user types
7. **Responsive Design**: Works on desktop, tablet, and mobile devices
8. **Blog Integration**: Links to Hugo blog deployed on Vercel

## File Structure

```
/mywebsite
├── index.html          # Landing page with command hints
├── whoami.html         # Bio page with personal information
├── portfolio.html      # Projects showcase page
├── styles.css          # All styling including themes
├── script.js           # Command system, theme switching, input handling
├── README.md           # User-facing documentation
├── AGENTS.md           # This file - maintenance guide
└── docs/
    └── plans/          # Implementation plans
```

## Architecture & Key Components

### 1. Command System (`script.js`)

**Available Commands:**
```javascript
const commands = {
    help: { description: 'Show available commands', execute: () => {...} },
    whoami: { description: 'Display information about me', execute: () => {...} },
    blog: { description: 'Visit my blog', execute: () => {...} },
    portfolio: { description: 'View my projects', execute: () => {...} },
    clear: { description: 'Clear the terminal', execute: () => {...} },
    home: { description: 'Return to home page', execute: () => {...} }
}
```

**How to Add New Commands:**
1. Add new entry to `commands` object
2. Define `description` and `execute` function
3. If creating a new page, create HTML file and navigate with `window.location.href`
4. If opening external link, use `window.open(url, '_blank')`
5. Update help text to include new command

### 2. Theme System (`script.js` + `styles.css`)

**Theme Definition** (`styles.css`):
- Each theme defined as CSS custom properties under `body[data-theme="name"]`
- Variables: `--bg-color`, `--text-color`, `--prompt-color`, `--cursor-color`, `--header-bg`, `--link-color`, `--label-color`

**Available Themes:**
- `classic` - Green on black
- `amber` - Orange on dark brown
- `white` - White text, green prompts
- `dracula` - Purple/pink theme
- `matrix` - Bright green Matrix-style

### 3. Page Structure

**index.html** - Landing page:
- Welcome message
- "Commands to try:" section with `whoami`, `blog`, `portfolio`
- Clear instruction: "↑ type a command and press Enter"
- Interactive command line

**whoami.html** - Bio page:
- ASCII art name banner
- Bio section (about, status)
- Links section (GitHub, X)
- Interactive command line at bottom

**portfolio.html** - Projects page:
- List of projects with descriptions and tech stack
- Links to GitHub repos and live demos
- Link to full GitHub profile

### 4. Terminal Header

All pages display: `michael@terminal:127.0.0.1~`

The `127.0.0.1` is a geeky reference to localhost ("there's no place like 127.0.0.1").

## Connected Blog

The portfolio links to a Hugo blog:

**Blog URL:** https://michaelguoblog.vercel.app
**Tech Stack:** Hugo + PaperMod theme + Vercel
**Blog Repo:** https://github.com/michaelpersonal/michaels-blog

**Blog Features:**
- Posts displayed directly on homepage
- Archive, Tags, Search pages
- Dark/light mode toggle
- Social links (GitHub, X)
- "Portfolio" button links back to terminal site

## Common Maintenance Tasks

### Update Bio Content

**File:** `whoami.html`

```html
<div class="bio-section">
    <p><span class="label">About:</span> Your new bio here</p>
    <p><span class="label">Status:</span> Your new status</p>
</div>
```

### Update Social Links

**File:** `whoami.html`

```html
<ul class="links-list">
    <li><a href="https://github.com/michaelpersonal" class="link" target="_blank">→ github</a></li>
    <li><a href="https://x.com/MichaelZSGuo" class="link" target="_blank">→ x</a></li>
</ul>
```

### Add New Project to Portfolio

**File:** `portfolio.html`

```html
<div class="project-item">
    <p class="project-name">→ <a href="URL" class="link" target="_blank">Project Name</a></p>
    <p class="project-desc">Project description here</p>
    <p class="project-tech">Tech / Stack / Used</p>
</div>
```

### Add New Blog Post

**In the blog repo (`michaels-blog`):**

```bash
cd ~/code/michaels-blog
hugo new posts/my-new-post.md
# Edit content/posts/my-new-post.md
git add . && git commit -m "Add new post" && git push
```

## Development Workflow

### Local Testing

```bash
cd ~/code/mywebsite
python3 -m http.server 8080
# Open http://localhost:8080
```

Test all commands: `help`, `whoami`, `blog`, `portfolio`, `clear`, `home`

### Deployment

Both sites auto-deploy on push to main branch:

```bash
# Portfolio
cd ~/code/mywebsite
git add . && git commit -m "description" && git push

# Blog
cd ~/code/michaels-blog
git add . && git commit -m "description" && git push
```

Vercel deploys in ~30 seconds.

## Code Conventions

### Naming
- CSS classes: kebab-case (`.command-line`, `.terminal-body`)
- JavaScript: camelCase (`executeCommand()`, `maintainFocus()`)

### CSS Variables
- All colors use CSS custom properties
- Theme-specific values under `body[data-theme="name"]`

### JavaScript
- No dependencies, pure vanilla JS
- Event-driven architecture
- Theme state persists in localStorage

## Social Links

- **GitHub:** https://github.com/michaelpersonal
- **X (Twitter):** https://x.com/MichaelZSGuo

## Version History

**v3.0** (Current) - January 2026
- Added `blog` command linking to Hugo blog
- Added `portfolio` page with projects
- Redesigned landing page with clear command hints
- Added geeky localhost IP to header
- Deployed to Vercel (previously GitHub Pages)
- Integrated with Hugo blog on separate Vercel project

**v2.0** - Interactive Terminal
- Command-based navigation system
- Dynamic input sizing
- Command history with arrow keys

**v1.0** - Static Terminal
- Initial design with typing animation
- Theme switching
- Static display only

---

Last Updated: 2026-01-15
Maintained with: Claude (Cursor Agent)
