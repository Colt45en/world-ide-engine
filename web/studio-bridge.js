/**
 * StudioBridge - Message passing system for component communication
 */

class StudioBridge {
    constructor() {
        this.listeners = {};
    }

    /**
     * Subscribe to messages from a specific source
     */
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    /**
     * Emit a message to all subscribers
     */
    emit(event, data) {
        console.log(`[Bridge] ${event}:`, data);
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    /**
     * Remove event listener
     */
    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
}

// Global bridge instance
const studioBridge = new StudioBridge();
