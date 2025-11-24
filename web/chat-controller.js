/**
 * ChatController - Command router and workflow coordinator
 */

class ChatController {
    constructor() {
        this.output = document.getElementById('chat-output');
        this.input = document.getElementById('chat-message');

        // Listen to bridge events
        studioBridge.on('engine:analyzed', (data) => this.handleEngineResult(data));
        studioBridge.on('recorder:marker', (data) => this.handleMarker(data));

        // Setup input handler
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.send();
        });

        this.addMessage('System initialized. Type "help" for commands.', 'system');
    }

    send() {
        const message = this.input.value.trim();
        if (!message) return;

        this.addMessage(`> ${message}`, 'user');
        this.input.value = '';

        this.processCommand(message);
    }

    processCommand(cmd) {
        const parts = cmd.toLowerCase().split(' ');
        const command = parts[0];

        switch (command) {
            case 'help':
                this.showHelp();
                break;

            case 'analyze':
                const text = parts.slice(1).join(' ');
                if (text) {
                    studioBridge.emit('chat:analyze', { text });
                } else {
                    this.addMessage('Usage: analyze <text>', 'error');
                }
                break;

            case 'record':
                studioBridge.emit('chat:record', { action: 'start' });
                break;

            case 'stop':
                studioBridge.emit('chat:record', { action: 'stop' });
                break;

            case 'marker':
                studioBridge.emit('chat:marker', { label: parts.slice(1).join(' ') || 'Marker' });
                break;

            case 'seeds':
                studioBridge.emit('chat:show-seeds', {});
                break;

            default:
                // Treat as analysis text
                studioBridge.emit('chat:analyze', { text: cmd });
        }
    }

    showHelp() {
        const helpText = `
Available Commands:
  help - Show this help
  analyze <text> - Analyze text semantically
  record - Start recording
  stop - Stop recording
  marker [label] - Add timeline marker
  seeds - Show all seed words
  
Or just type text to analyze it directly.
        `.trim();
        this.addMessage(helpText, 'system');
    }

    handleEngineResult(data) {
        const score = data.sentiment_score || 0;
        const msg = `Analysis complete. Sentiment: ${score.toFixed(3)}`;
        this.addMessage(msg, 'system');
    }

    handleMarker(data) {
        this.addMessage(`Marker added: ${data.label}`, 'system');
    }

    addMessage(text, type = 'user') {
        const msg = document.createElement('div');
        msg.className = `message ${type}`;
        msg.textContent = text;
        this.output.appendChild(msg);
        this.output.scrollTop = this.output.scrollHeight;
    }
}

// Initialize controller
const chatController = new ChatController();
