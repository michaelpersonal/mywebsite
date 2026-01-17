# Hugo Blog + Vercel Deployment Implementation Plan

> ✅ **STATUS: COMPLETE** (2026-01-16)
> - Phase 1: Hugo Blog Setup ✅
> - Phase 2: Deploy to Vercel ✅
> - Phase 3: Link Portfolio to Blog ✅
> - Bonus: Notion Sync (see `michaels-blog/docs/plans/2026-01-15-notion-sync.md`) ✅

**Goal:** Create a Hugo blog (like lilianweng.github.io) with PaperMod theme, deploy to Vercel, and link it to the existing terminal portfolio.

**Architecture:** Two separate repositories — portfolio stays at `mywebsite/`, new blog at `michaels-blog/`. Both deploy independently to Vercel. Portfolio links to blog via a new `blog` command.

**Tech Stack:** Hugo (static site generator), PaperMod theme, Vercel (hosting), Git, Markdown

---

## Phase 1: Hugo Blog Setup

### Task 1: Install Hugo

**Prerequisites:** Homebrew installed on macOS

**Step 1: Check if Hugo is already installed**

Run:
```bash
hugo version
```
Expected: Either version info (skip to Task 2) or "command not found" (continue)

**Step 2: Install Hugo via Homebrew**

Run:
```bash
brew install hugo
```
Expected: Installation completes successfully

**Step 3: Verify installation**

Run:
```bash
hugo version
```
Expected: `hugo v0.1XX.X+extended...` (version number)

---

### Task 2: Create Hugo Site Structure

**Files:**
- Create: `~/code/michaels-blog/` (entire site structure)

**Step 1: Create new Hugo site**

Run:
```bash
cd ~/code
hugo new site michaels-blog
cd michaels-blog
```
Expected: "Congratulations! Your new Hugo site is created..."

**Step 2: Initialize Git repository**

Run:
```bash
git init
```
Expected: "Initialized empty Git repository..."

**Step 3: Verify structure**

Run:
```bash
ls -la
```
Expected: Directories including `archetypes/`, `content/`, `layouts/`, `static/`, `themes/`, and file `hugo.toml`

---

### Task 3: Install PaperMod Theme

**Files:**
- Create: `~/code/michaels-blog/themes/PaperMod/` (as git submodule)

**Step 1: Add PaperMod as git submodule**

Run:
```bash
cd ~/code/michaels-blog
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```
Expected: Cloning into 'themes/PaperMod'...

**Step 2: Verify theme installed**

Run:
```bash
ls themes/PaperMod/
```
Expected: Files including `LICENSE`, `README.md`, `theme.toml`, directories `layouts/`, `assets/`

---

### Task 4: Configure Hugo Site

**Files:**
- Modify: `~/code/michaels-blog/hugo.toml`

**Step 1: Replace default config with full configuration**

Create file `hugo.toml` with this content:

```toml
baseURL = "https://michaels-blog.vercel.app/"
languageCode = "en-us"
title = "Michael's Blog"
theme = "PaperMod"

# Enable emoji support
enableEmoji = true

# Generate robots.txt
enableRobotsTXT = true

# Build settings
buildDrafts = false
buildFuture = false
buildExpired = false

# Pagination
paginate = 10

# Minify output
minify = true

[params]
  # Site description
  description = "Learning notes and thoughts"
  author = "Michael"
  
  # Show reading time
  ShowReadingTime = true
  
  # Show share buttons
  ShowShareButtons = true
  
  # Show post navigation
  ShowPostNavLinks = true
  
  # Show breadcrumbs
  ShowBreadCrumbs = true
  
  # Show code copy buttons
  ShowCodeCopyButtons = true
  
  # Show table of contents
  ShowToc = true
  
  # Default theme (light/dark/auto)
  defaultTheme = "auto"
  
  # Home page profile
  [params.profileMode]
    enabled = true
    title = "Michael's Blog"
    subtitle = "Learning notes and thoughts on tech"
    imageUrl = ""
    imageTitle = ""
    [[params.profileMode.buttons]]
      name = "Posts"
      url = "/posts/"
    [[params.profileMode.buttons]]
      name = "Portfolio"
      url = "https://michael-terminal.vercel.app"

  # Social icons
  [[params.socialIcons]]
    name = "github"
    url = "https://github.com/michaelpersonal"
  [[params.socialIcons]]
    name = "linkedin"
    url = "https://linkedin.com/in/"
  [[params.socialIcons]]
    name = "email"
    url = "mailto:your@email.com"

# Main menu
[menu]
  [[menu.main]]
    identifier = "posts"
    name = "Posts"
    url = "/posts/"
    weight = 10
  [[menu.main]]
    identifier = "archive"
    name = "Archive"
    url = "/archive/"
    weight = 20
  [[menu.main]]
    identifier = "tags"
    name = "Tags"
    url = "/tags/"
    weight = 30
  [[menu.main]]
    identifier = "search"
    name = "Search"
    url = "/search/"
    weight = 40

# Syntax highlighting
[markup]
  [markup.highlight]
    style = "dracula"
    lineNos = false
    codeFences = true
    guessSyntax = true

# Output formats for search
[outputs]
  home = ["HTML", "RSS", "JSON"]
```

**Step 2: Verify config is valid**

Run:
```bash
cd ~/code/michaels-blog
hugo config
```
Expected: Shows parsed configuration without errors

---

### Task 5: Create Archive Page

**Files:**
- Create: `~/code/michaels-blog/content/archive.md`

**Step 1: Create archive page**

Create file `content/archive.md`:

```markdown
---
title: "Archive"
layout: "archives"
url: "/archive/"
summary: "archive"
---
```

---

### Task 6: Create Search Page

**Files:**
- Create: `~/code/michaels-blog/content/search.md`

**Step 1: Create search page**

Create file `content/search.md`:

```markdown
---
title: "Search"
layout: "search"
url: "/search/"
summary: "search"
placeholder: "Search posts..."
---
```

---

### Task 7: Create First Blog Post

**Files:**
- Create: `~/code/michaels-blog/content/posts/hello-world.md`

**Step 1: Create posts directory**

Run:
```bash
mkdir -p ~/code/michaels-blog/content/posts
```

**Step 2: Create first post**

Create file `content/posts/hello-world.md`:

```markdown
---
title: "Hello World"
date: 2026-01-15
draft: false
tags: ["intro", "blog"]
categories: ["General"]
summary: "Welcome to my blog! This is my first post."
---

## Welcome!

This is my first blog post. I'll be sharing my learning notes and thoughts here.

### What to Expect

- Technical deep dives
- Learning notes
- Project updates
- Random thoughts

### About This Blog

This blog is built with [Hugo](https://gohugo.io/) using the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme, and deployed on [Vercel](https://vercel.com).

Feel free to explore and check out my [portfolio](https://michael-terminal.vercel.app) for more about me.

## Code Example

Here's a simple code block to test syntax highlighting:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

Thanks for reading!
```

---

### Task 8: Test Hugo Site Locally

**Step 1: Start Hugo development server**

Run:
```bash
cd ~/code/michaels-blog
hugo server -D
```
Expected: "Web Server is available at http://localhost:1313/"

**Step 2: Open in browser and verify**

Open: `http://localhost:1313/`

Expected:
- Home page shows with PaperMod theme
- "Posts" button links to posts list
- First post "Hello World" is visible
- Dark/light mode toggle works
- Search page works

**Step 3: Stop server**

Press: `Ctrl+C`

---

### Task 9: Initial Git Commit

**Step 1: Create .gitignore**

Create file `.gitignore`:

```
# Hugo build output
public/
resources/_gen/

# Hugo lock file
.hugo_build.lock

# OS files
.DS_Store
Thumbs.db

# IDE
.idea/
.vscode/
*.swp
*.swo
```

**Step 2: Stage all files**

Run:
```bash
cd ~/code/michaels-blog
git add .
```

**Step 3: Commit**

Run:
```bash
git commit -m "Initial commit: Hugo blog with PaperMod theme

- Hugo site structure
- PaperMod theme as submodule
- Site configuration (hugo.toml)
- Archive and Search pages
- First blog post: Hello World"
```
Expected: Commit created successfully

---

## Phase 2: Deploy to Vercel

### Task 10: Create GitHub Repository

**Step 1: Create new repository on GitHub**

Go to: https://github.com/new

Settings:
- Repository name: `michaels-blog`
- Description: "My personal blog built with Hugo"
- Public or Private: Your choice
- Do NOT initialize with README (we already have content)

**Step 2: Add remote and push**

Run:
```bash
cd ~/code/michaels-blog
git remote add origin https://github.com/YOUR_USERNAME/michaels-blog.git
git branch -M main
git push -u origin main
```
Expected: Push successful

---

### Task 11: Deploy to Vercel

**Step 1: Go to Vercel**

Open: https://vercel.com/new

**Step 2: Import GitHub repository**

- Click "Import Git Repository"
- Select `michaels-blog` repository
- Click "Import"

**Step 3: Configure build settings**

Vercel should auto-detect Hugo, but verify:
- Framework Preset: `Hugo`
- Build Command: `hugo --gc --minify`
- Output Directory: `public`
- Install Command: (leave empty)

**Step 4: Set Hugo version environment variable**

Add Environment Variable:
- Name: `HUGO_VERSION`
- Value: `0.121.0` (or your installed version from `hugo version`)

**Step 5: Deploy**

Click "Deploy"

Expected: Build succeeds, site is live at `michaels-blog.vercel.app` (or similar)

**Step 6: Verify deployment**

Open the Vercel URL and verify:
- Site loads correctly
- Theme displays properly
- Posts are accessible
- Search works

---

## Phase 3: Link Portfolio to Blog

### Task 12: Add Blog Command to Portfolio

**Files:**
- Modify: `~/code/mywebsite/script.js`

**Step 1: Add blog command to commands object**

In `script.js`, add to the `commands` object (after line 52, before the closing `}`):

```javascript
    blog: {
        description: 'Visit my blog',
        execute: () => {
            window.open('https://michaels-blog.vercel.app', '_blank');
            return 'Opening blog in new tab...';
        }
    }
```

**Step 2: Update help command output**

In `script.js`, update the help execute function (around line 16-26) to include blog:

```javascript
    help: {
        description: 'Show available commands',
        execute: () => {
            return `
Available commands:
  help      - Show this help message
  whoami    - Display information about me
  blog      - Visit my blog
  clear     - Clear the terminal
  home      - Return to home page

Keyboard shortcuts:
  Shift+Tab - Cycle through color themes
  Up/Down   - Navigate command history
            `;
        }
    },
```

**Step 3: Verify locally**

Open `index.html` in browser, type `help`, verify blog command is listed.
Type `blog`, verify it opens the blog in a new tab.

---

### Task 13: Commit and Deploy Portfolio Update

**Step 1: Stage changes**

Run:
```bash
cd ~/code/mywebsite
git add script.js
```

**Step 2: Commit**

Run:
```bash
git commit -m "feat: add blog command to terminal

Links to Hugo blog deployed on Vercel"
```

**Step 3: Push to GitHub**

Run:
```bash
git push
```

Expected: GitHub Pages (or Vercel) auto-deploys

---

## Phase 4: Deploy Portfolio to Vercel (Optional)

### Task 14: Deploy Portfolio to Vercel

**Note:** Skip this task if you want to keep portfolio on GitHub Pages.

**Step 1: Go to Vercel**

Open: https://vercel.com/new

**Step 2: Import mywebsite repository**

- Click "Import Git Repository"
- Select `mywebsite` repository
- Click "Import"

**Step 3: Configure build settings**

- Framework Preset: `Other`
- Build Command: (leave empty - static site)
- Output Directory: `.` (root)
- Install Command: (leave empty)

**Step 4: Deploy**

Click "Deploy"

Expected: Site is live at `mywebsite.vercel.app` or `michael-terminal.vercel.app`

**Step 5: Update blog config**

If portfolio URL changed, update `hugo.toml` in the blog to point to new URL:

```toml
[[params.profileMode.buttons]]
  name = "Portfolio"
  url = "https://YOUR-NEW-VERCEL-URL.vercel.app"
```

---

## Phase 5: Set Up Superpowers Rules for Blog (Optional)

### Task 15: Add Superpowers Rules to Blog

**Step 1: Create .cursor directory**

Run:
```bash
mkdir -p ~/code/michaels-blog/.cursor
```

**Step 2: Create symlink to shared rules**

Run:
```bash
ln -s ../../.cursor/rules ~/code/michaels-blog/.cursor/rules
```

**Step 3: Verify**

Run:
```bash
ls ~/code/michaels-blog/.cursor/rules/
```
Expected: Lists all superpowers .mdc files

---

## Summary

After completing all tasks:

| Site | URL | Tech |
|------|-----|------|
| Portfolio | `michael-terminal.vercel.app` | HTML/CSS/JS |
| Blog | `michaels-blog.vercel.app` | Hugo + PaperMod |

| Command | Action |
|---------|--------|
| `blog` | Opens blog in new tab |
| `whoami` | Shows portfolio bio |
| `help` | Lists all commands |

---

## Future Enhancements

- [ ] Custom domain for both sites
- [ ] Add more blog posts
- [ ] Add comments (Giscus/Disqus)
- [ ] Add analytics (Vercel Analytics)
- [ ] RSS feed configuration
- [ ] Social sharing images (og:image)
