// Interactive Terminal with Command System

// Theme management
const themes = ['classic', 'amber', 'white', 'dracula', 'matrix'];
let currentThemeIndex = 0;

// Command history
let commandHistory = [];
let historyIndex = -1;

// Available commands
const commands = {
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
    whoami: {
        description: 'Display information about me',
        execute: () => {
            window.location.href = 'whoami.html';
            return null;
        }
    },
    clear: {
        description: 'Clear the terminal',
        execute: () => {
            const content = document.getElementById('content');
            const commandLine = content.querySelector('.command-line');
            content.innerHTML = '';
            content.appendChild(commandLine);
            return null;
        }
    },
    home: {
        description: 'Return to home page',
        execute: () => {
            window.location.href = 'index.html';
            return null;
        }
    },
    blog: {
        description: 'Visit my blog',
        execute: () => {
            window.open('https://michaels-blog.vercel.app', '_blank');
            return 'Opening blog in new tab...';
        }
    }
};

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

// Add command to history display
function addToHistory(command, output) {
    const content = document.getElementById('content');
    const commandLine = content.querySelector('.command-line');

    // Create history entry
    const historyEntry = document.createElement('div');
    historyEntry.className = 'history-line';

    const promptSpan = document.createElement('span');
    promptSpan.className = 'prompt';
    promptSpan.textContent = 'michael@portfolio:~$';

    const commandSpan = document.createElement('span');
    commandSpan.className = 'command';
    commandSpan.textContent = ' ' + command;

    historyEntry.appendChild(promptSpan);
    historyEntry.appendChild(commandSpan);

    content.insertBefore(historyEntry, commandLine);

    // Add output if exists
    if (output) {
        const outputDiv = document.createElement('div');
        outputDiv.className = output.isError ? 'error-message' : 'success-message';
        outputDiv.innerHTML = output.text.replace(/\n/g, '<br>');
        content.insertBefore(outputDiv, commandLine);
    }

    // Scroll to bottom
    const terminalBody = document.querySelector('.terminal-body');
    terminalBody.scrollTop = terminalBody.scrollHeight;
}

// Execute command
function executeCommand(input) {
    const trimmedInput = input.trim();

    if (!trimmedInput) {
        return;
    }

    // Add to command history
    commandHistory.push(trimmedInput);
    historyIndex = commandHistory.length;

    const parts = trimmedInput.split(' ');
    const command = parts[0].toLowerCase();

    if (commands[command]) {
        const result = commands[command].execute();
        if (result !== null) {
            addToHistory(trimmedInput, { text: result, isError: false });
        } else {
            addToHistory(trimmedInput, null);
        }
    } else {
        addToHistory(trimmedInput, {
            text: `Command not found: ${command}\nType 'help' to see available commands.`,
            isError: true
        });
    }
}

// Auto-resize input based on content
function resizeInput(input) {
    const value = input.value;
    const length = value.length;
    input.style.width = (Math.max(2, length + 1)) + 'ch';
}

// Handle input
function handleInput(event) {
    const input = event.target;
    const key = event.key;

    if (key === 'Enter') {
        const command = input.value;
        executeCommand(command);
        input.value = '';
        resizeInput(input);
    } else if (key === 'ArrowUp') {
        event.preventDefault();
        if (historyIndex > 0) {
            historyIndex--;
            input.value = commandHistory[historyIndex];
            resizeInput(input);
        }
    } else if (key === 'ArrowDown') {
        event.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            input.value = commandHistory[historyIndex];
            resizeInput(input);
        } else {
            historyIndex = commandHistory.length;
            input.value = '';
            resizeInput(input);
        }
    } else if (key === 'Tab' && event.shiftKey) {
        event.preventDefault();
        cycleTheme();
    } else {
        // Resize on any other key (typing)
        setTimeout(() => resizeInput(input), 0);
    }
}

// Keep focus on input
function maintainFocus() {
    const input = document.getElementById('command-input');
    if (input && document.activeElement !== input) {
        input.focus();
    }
}

// Initialize terminal
function initTerminal() {
    const input = document.getElementById('command-input');

    if (input) {
        input.addEventListener('keydown', handleInput);
        resizeInput(input);
        input.focus();

        // Keep input focused when clicking anywhere in terminal
        document.addEventListener('click', maintainFocus);

        // Refocus periodically to handle edge cases
        setInterval(maintainFocus, 100);
    }
}

// Start everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTerminal();
});
