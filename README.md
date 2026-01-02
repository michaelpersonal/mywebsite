# Michael's Terminal Portfolio

A minimalist personal website with a terminal/CLI aesthetic inspired by bentossell.com.

## Features

- **Terminal UI**: Clean, retro command-line interface design
- **Typing Animation**: Simulated terminal typing effect on page load
- **5 Color Themes**: Cycle through classic terminal color schemes
  - Classic (green on black)
  - Amber (vintage monitor)
  - White (high contrast)
  - Dracula (modern dark theme)
  - Matrix (green glow)
- **Theme Switcher**: Press `Shift+Tab` to cycle through themes
- **Fully Responsive**: Works on desktop, tablet, and mobile
- **Lightweight**: Pure HTML, CSS, and vanilla JavaScript (no frameworks)

## File Structure

```
/mywebsite
├── index.html          # Main HTML structure
├── styles.css          # Terminal styling and themes
├── script.js           # Typing animation & theme switching
└── README.md           # This file
```

## How to Use

1. **View Locally**: Simply open `index.html` in your web browser
2. **Edit Content**: Modify the bio and links in `index.html` (lines 40-60)
3. **Customize Themes**: Adjust colors in `styles.css` (lines 16-64)
4. **Change Animation**: Tweak typing speed in `script.js` (line 47)

## Customization Guide

### Update Your Bio
Edit the content in `index.html`:
```html
<div class="bio-section">
    <p><span class="label">About:</span> Your description here</p>
    <p><span class="label">Status:</span> Your status here</p>
</div>
```

### Add Real Links
Replace the `#` placeholders with your actual URLs:
```html
<li><a href="https://github.com/yourusername" class="link">→ github</a></li>
```

### Modify Themes
Add or edit color schemes in `styles.css`:
```css
body[data-theme="yourtheme"] {
    --bg-color: #000000;
    --text-color: #00ff00;
    /* ... more colors */
}
```

## Deployment Options

### GitHub Pages (Free)
1. Create a new GitHub repository
2. Push these files to the repository
3. Go to Settings → Pages
4. Select your main branch as the source
5. Your site will be live at `https://yourusername.github.io/repo-name`

### Netlify (Free)
1. Drag and drop the folder at netlify.com/drop
2. Get an instant live URL

### Vercel (Free)
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project directory
3. Follow the prompts

## Browser Support

Works in all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Keyboard Shortcuts

- `Shift+Tab`: Cycle through color themes

## Credits

Inspired by [bentossell.com](https://www.bentossell.com/)
