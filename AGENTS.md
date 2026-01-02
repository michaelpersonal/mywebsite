# AGENTS.md - Project Maintenance Guide

This document provides context for AI agents and developers working on Michael's terminal-style portfolio website.

## Project Overview

A minimalist personal portfolio website with an interactive terminal/CLI aesthetic, inspired by bentossell.com. Built with pure HTML, CSS, and vanilla JavaScript (no frameworks).

**Live Site:** https://michaelpersonal.github.io/mywebsite/
**Repository:** https://github.com/michaelpersonal/mywebsite

## Core Features

1. **Interactive Terminal Interface**: Real command-line input where users can type commands
2. **Command System**: Navigate between pages using terminal commands (`whoami`, `help`, `clear`, `home`)
3. **Theme Switcher**: 5 color themes (classic, amber, white, dracula, matrix) - cycle with `Shift+Tab`
4. **Command History**: Navigate previous commands with up/down arrow keys
5. **Dynamic Input Sizing**: Input field expands as user types
6. **Responsive Design**: Works on desktop, tablet, and mobile devices

## File Structure

```
/mywebsite
├── index.html          # Main landing page with interactive terminal
├── whoami.html         # Bio page with personal information
├── styles.css          # All styling including themes
├── script.js           # Command system, theme switching, input handling
├── README.md           # User-facing documentation
└── AGENTS.md           # This file - maintenance guide
```

## Architecture & Key Components

### 1. Command System (`script.js`)

**Commands Object** (lines 12-53):
```javascript
const commands = {
    help: { description: '...', execute: () => {...} },
    whoami: { description: '...', execute: () => {...} },
    clear: { description: '...', execute: () => {...} },
    home: { description: '...', execute: () => {...} }
}
```

**How to Add New Commands:**
1. Add new entry to `commands` object
2. Define `description` and `execute` function
3. If creating a new page, create HTML file and navigate with `window.location.href`
4. Update help text to include new command

**Example - Adding a "projects" command:**
```javascript
projects: {
    description: 'View my projects',
    execute: () => {
        window.location.href = 'projects.html';
        return null;
    }
}
```

### 2. Theme System (`script.js` + `styles.css`)

**Theme Definition** (`styles.css` lines 18-64):
- Each theme defined as CSS custom properties under `body[data-theme="name"]`
- Variables: `--bg-color`, `--text-color`, `--prompt-color`, `--cursor-color`, `--header-bg`, `--link-color`, `--label-color`

**How to Add New Theme:**
1. Add theme name to `themes` array in `script.js` (line 4)
2. Add CSS variables in `styles.css`:
```css
body[data-theme="newtheme"] {
    --bg-color: #000000;
    --text-color: #00ff00;
    --prompt-color: #00ff00;
    --cursor-color: #00ff00;
    --header-bg: #1a1a1a;
    --link-color: #00cc00;
    --label-color: #00ff00;
}
```

### 3. Input Handling (`script.js`)

**Key Functions:**
- `handleInput(event)`: Processes keyboard events (Enter, arrows, Shift+Tab)
- `resizeInput(input)`: Dynamically adjusts input width as user types
- `executeCommand(input)`: Parses and executes commands
- `addToHistory(command, output)`: Adds executed commands to terminal display
- `maintainFocus()`: Keeps input focused for seamless typing experience

**Critical Detail:** Input field uses `width: 2ch` minimum and expands via JavaScript. The cursor `█` appears immediately after the input field.

### 4. Page Structure

**index.html** - Landing page:
- Welcome message
- Interactive command line
- Empty on load, prompts user to type commands

**whoami.html** - Bio page:
- ASCII art name banner
- Bio section (about, status)
- Links section (github, linkedin, email, twitter)
- Interactive command line at bottom for navigation back

## Common Maintenance Tasks

### Update Bio Content

**File:** `whoami.html` (lines 33-54)

```html
<div class="bio-section">
    <p><span class="label">About:</span> Your new bio here</p>
    <p><span class="label">Status:</span> Your new status</p>
</div>
```

### Update Links

**File:** `whoami.html` (lines 47-54)

Replace `#` with actual URLs:
```html
<li><a href="https://github.com/username" class="link">→ github</a></li>
```

### Add New Page

1. Create new HTML file (e.g., `projects.html`)
2. Copy structure from `whoami.html`
3. Modify content section
4. Add command to `script.js` commands object
5. Update help text to include new command
6. Test locally before committing

### Modify Terminal Prompt

**Change prompt text:**
- `index.html` line 32: `<span class="prompt">michael@portfolio:~$</span>`
- `whoami.html` line 19: `<span class="prompt">michael@portfolio:~$</span>`
- `script.js` line 87: `promptSpan.textContent = 'michael@portfolio:~$';`

Update all three locations for consistency.

### Change Typing Speed (if animation is added)

Search for `setTimeout` delays in `script.js` and adjust millisecond values.

## Development Workflow

### Local Testing

1. Open `index.html` directly in browser
2. Test all commands: `help`, `whoami`, `clear`, `home`
3. Test theme switching with `Shift+Tab`
4. Test command history with up/down arrows
5. Test on mobile viewport (browser DevTools responsive mode)

### Deployment to GitHub Pages

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Description of changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push

# Wait 1-2 minutes for GitHub Pages deployment
# Hard refresh browser to clear cache: Cmd/Ctrl + Shift + R
```

**Important:** Browser caching can make changes appear not to work. Always do a hard refresh after deployment.

## Code Conventions

### Naming
- Use kebab-case for CSS classes: `.command-line`, `.terminal-body`
- Use camelCase for JavaScript: `executeCommand()`, `maintainFocus()`
- Use descriptive names: `resizeInput()` not `resize()`

### Formatting
- Indentation: 4 spaces (HTML, CSS, JS)
- Line length: No strict limit, but keep readable
- Comments: Add for non-obvious functionality

### CSS Variables
- All colors use CSS custom properties (CSS variables)
- Theme-specific values defined under `body[data-theme="name"]`
- Reference variables with `var(--variable-name)`

### JavaScript
- No dependencies, pure vanilla JS
- Event-driven architecture
- Functions are modular and single-purpose
- Theme state persists in localStorage
- Command history stored in memory (resets on page reload)

## Troubleshooting

### Cursor appears on far right
- Check `styles.css` `.command-input` has `width: 2ch` not `flex: 1`
- Verify `resizeInput()` function exists in `script.js`
- Hard refresh browser to clear cache

### Commands not working
- Check browser console for JavaScript errors (F12)
- Verify `script.js` is loading (check Network tab)
- Confirm input element has `id="command-input"`

### Themes not switching
- Check localStorage permissions in browser
- Verify theme names in `themes` array match CSS selectors
- Check that `Shift+Tab` isn't captured by browser/OS

### Page navigation broken
- Check that HTML files exist in same directory
- Verify `window.location.href` uses correct filenames
- Check for typos in file extensions (.html)

### Styles not updating on GitHub Pages
- **Most common issue:** Browser cache
- Solution: Hard refresh (Cmd/Ctrl + Shift + R)
- Alternative: Clear browser cache manually
- Verify files deployed: Check raw file URLs on GitHub

## Technical Decisions & Rationale

### Why No Framework?
- Simplicity: Easy to understand and maintain
- Performance: Minimal load time, no bundle size
- Portability: Works anywhere, no build step
- Learning: Clear demonstration of vanilla JS skills

### Why No Build Process?
- Direct deployment to GitHub Pages
- No compilation or transpilation needed
- Easier for non-developers to understand
- Faster iteration during development

### Why localStorage for Themes?
- Persists user preference across sessions
- Simple key-value storage, no backend needed
- Graceful degradation if disabled

### Why Command-Based Navigation?
- Unique, memorable user experience
- Showcases technical aesthetic
- Interactive engagement vs static links
- Inspired by bentossell.com design philosophy

## Future Enhancement Ideas

### Easy Additions
- Add more commands: `contact`, `projects`, `blog`, `resume`
- Add ASCII art variations for different pages
- Add command aliases (e.g., `ls` for `help`)
- Add tab completion for commands
- Add `history` command to show past commands

### Medium Complexity
- Add typing animation on page load
- Add sound effects for commands (optional, off by default)
- Add easter eggs for specific commands
- Add RSS feed integration for blog posts
- Add GitHub API integration to show real projects

### Advanced Features
- Command arguments (e.g., `theme --list`, `theme amber`)
- File system simulation (virtual directories)
- Pipe commands together (e.g., `help | grep theme`)
- Vim-mode text editing
- Persistent command history (localStorage)
- Search functionality across all pages

## Browser Support

**Tested and working:**
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

**Required features:**
- CSS custom properties (CSS variables)
- ES6 JavaScript (arrow functions, const/let, template literals)
- localStorage API
- flexbox layout

## Performance Notes

- No external dependencies = fast load time
- Minimal JavaScript = quick execution
- CSS-only animations for smooth performance
- Font is system-installed (Courier New) = no web font loading

## Accessibility Considerations

**Current State:**
- Semantic HTML structure
- High contrast themes available
- Keyboard-only navigation possible
- Text-based interface (screen reader compatible)

**Known Limitations:**
- No ARIA labels on interactive elements
- Command system requires typing ability
- No skip-to-content link
- Visual cursor indicator only

**Improvements to Consider:**
- Add ARIA landmarks
- Add visible focus indicators
- Add screen reader announcements for command results
- Consider adding clickable command shortcuts for mobile

## Contact & Ownership

**Site Owner:** Michael
**Repository:** https://github.com/michaelpersonal/mywebsite
**Hosting:** GitHub Pages
**Domain:** michaelpersonal.github.io/mywebsite

## Version History

**v2.0** (Current) - Interactive Terminal
- Command-based navigation system
- Dynamic input sizing
- Command history with arrow keys

**v1.0** - Static Terminal
- Initial design with typing animation
- Theme switching
- Static display only

---

Last Updated: 2026-01-01
Maintained with: Claude Code (claude-sonnet-4-5)
