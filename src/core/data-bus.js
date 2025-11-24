/**
 * DataBus - Central communication hub for all subsystems
 * Enables scalable data sharing across the entire world engine
 */

class DataBus {
  constructor() {
    this.subscribers = new Map();
    this.messageHistory = [];
    this.maxHistorySize = 1000;
    this.stats = {
      messagesSent: 0,
      subscribersCount: 0
    };
  }
  
  /**
   * Subscribe to events on the data bus
   * @param {string} channel - Channel name or '*' for all channels
   * @param {Function} callback - Function to call when message is published
   * @returns {Function} Unsubscribe function
   */
  subscribe(channel, callback) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    
    this.subscribers.get(channel).add(callback);
    this.stats.subscribersCount = this.getTotalSubscribers();
    
    // Return unsubscribe function
    return () => {
      const channelSubs = this.subscribers.get(channel);
      if (channelSubs) {
        channelSubs.delete(callback);
        if (channelSubs.size === 0) {
          this.subscribers.delete(channel);
        }
      }
      this.stats.subscribersCount = this.getTotalSubscribers();
    };
  }
  
  /**
   * Publish a message to a channel
   * @param {string} channel - Channel name
   * @param {any} data - Data to publish
   */
  publish(channel, data) {
    const message = {
      channel,
      data,
      timestamp: Date.now()
    };
    
    // Store in history
    this.messageHistory.push(message);
    if (this.messageHistory.length > this.maxHistorySize) {
      this.messageHistory.shift();
    }
    
    this.stats.messagesSent++;
    
    // Notify channel-specific subscribers
    const channelSubs = this.subscribers.get(channel);
    if (channelSubs) {
      channelSubs.forEach(callback => {
        try {
          callback(data, channel);
        } catch (error) {
          console.error(`Error in subscriber for ${channel}:`, error);
        }
      });
    }
    
    // Notify wildcard subscribers
    const wildcardSubs = this.subscribers.get('*');
    if (wildcardSubs) {
      wildcardSubs.forEach(callback => {
        try {
          callback(data, channel);
        } catch (error) {
          console.error(`Error in wildcard subscriber:`, error);
        }
      });
    }
  }
  
  /**
   * Get statistics about the data bus
   */
  getStats() {
    return {
      ...this.stats,
      channels: Array.from(this.subscribers.keys()),
      historySize: this.messageHistory.length
    };
  }
  
  /**
   * Get total number of subscribers across all channels
   */
  getTotalSubscribers() {
    let total = 0;
    this.subscribers.forEach(subs => {
      total += subs.size;
    });
    return total;
  }
  
  /**
   * Clear all subscribers and history
   */
  clear() {
    this.subscribers.clear();
    this.messageHistory = [];
    this.stats.subscribersCount = 0;
  }
  
  /**
   * Get message history for a specific channel
   */
  getHistory(channel = null, limit = 100) {
    let history = this.messageHistory;
    if (channel) {
      history = history.filter(msg => msg.channel === channel);
    }
    return history.slice(-limit);
  }
}

export { DataBus };
