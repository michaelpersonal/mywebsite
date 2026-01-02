// Terminal Typing Animation and Theme Switcher

// Theme management
const themes = ['classic', 'amber', 'white', 'dracula', 'matrix'];
let currentThemeIndex = 0;

// Initialize theme
function initTheme() {
    const savedTheme = localStorage.getItem('terminalTheme');
    if (savedTheme && themes.includes(savedTheme)) {
        currentThemeIndex = themes.indexOf(savedTheme);
    }
    applyTheme();
}

// Apply current theme
function applyTheme() {
    document.body.setAttribute('data-theme', themes[currentThemeIndex]);
    localStorage.setItem('terminalTheme', themes[currentThemeIndex]);
}

// Cycle to next theme
function cycleTheme() {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    applyTheme();
}

// Keyboard event listener for theme switching
document.addEventListener('keydown', (e) => {
    // Shift + Tab to cycle themes
    if (e.shiftKey && e.key === 'Tab') {
        e.preventDefault();
        cycleTheme();
    }
});

// Typing animation
function typeCommand(text, element, speed = 100) {
    return new Promise((resolve) => {
        let i = 0;
        const cursor = document.getElementById('cursor');

        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            } else {
                // Remove typing cursor, show output
                cursor.style.display = 'none';
                resolve();
            }
        }

        type();
    });
}

// Show output with fade-in effect
function showOutput() {
    const output = document.getElementById('output');
    output.classList.remove('hidden');
    output.classList.add('fade-in');
}

// Initialize terminal on page load
async function initTerminal() {
    const commandElement = document.getElementById('initial-command');
    const command = 'cat about.txt';

    // Wait a bit before starting to type
    await new Promise(resolve => setTimeout(resolve, 500));

    // Type the command
    await typeCommand(command, commandElement, 80);

    // Wait a moment, then show output
    await new Promise(resolve => setTimeout(resolve, 300));
    showOutput();
}

// Start everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTerminal();
});

// Easter egg: type 'help' command (future enhancement)
document.addEventListener('keypress', (e) => {
    // Could add interactive command input here in the future
});
