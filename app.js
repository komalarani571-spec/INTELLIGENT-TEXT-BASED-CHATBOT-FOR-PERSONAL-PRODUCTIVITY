// Chatbot Application JavaScript
class ChatbotApp {
    constructor() {
        this.socket = null;
        this.sessionId = this.generateSessionId();
        this.userId = 1; // Default user for demo
        this.isConnected = false;
        this.isTyping = false;
        
        // DOM elements
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendButton'),
            typingIndicator: document.getElementById('typingIndicator'),
            connectionStatus: document.getElementById('connectionStatus'),
            clearChat: document.getElementById('clearChat'),
            showAnalytics: document.getElementById('showAnalytics'),
            analyticsModal: document.getElementById('analyticsModal'),
            closeAnalytics: document.getElementById('closeAnalytics'),
            analyticsContent: document.getElementById('analyticsContent'),
            errorToast: document.getElementById('errorToast'),
            successToast: document.getElementById('successToast'),
            errorMessage: document.getElementById('errorMessage'),
            successMessage: document.getElementById('successMessage')
        };
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.bindEvents();
        this.loadChatHistory();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    initializeSocket() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                timeout: 5000,
                query: {
                    session_id: this.sessionId
                }
            });
            
            // Socket event handlers
            this.socket.on('connect', () => {
                this.isConnected = true;
                this.updateConnectionStatus('Connected', 'connected');
                console.log('Connected to chatbot server');
            });
            
            this.socket.on('disconnect', () => {
                this.isConnected = false;
                this.updateConnectionStatus('Disconnected', 'disconnected');
                console.log('Disconnected from chatbot server');
            });
            
            this.socket.on('connect_error', (error) => {
                this.isConnected = false;
                this.updateConnectionStatus('Connection Error', 'disconnected');
                console.error('Connection error:', error);
                this.showError('Failed to connect to chatbot server');
            });
            
            this.socket.on('message', (data) => {
                this.handleBotResponse(data);
            });
            
            this.socket.on('typing', (data) => {
                if (data.typing) {
                    this.showTypingIndicator();
                } else {
                    this.hideTypingIndicator();
                }
            });
            
            this.socket.on('error', (data) => {
                this.showError(data.message || 'An error occurred');
                this.hideTypingIndicator();
            });
            
        } catch (error) {
            console.error('Socket initialization error:', error);
            this.showError('Failed to initialize chat connection');
        }
    }
    
    bindEvents() {
        // Send message on button click
        this.elements.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send message on Enter key press
        this.elements.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input field focus and blur events
        this.elements.messageInput.addEventListener('focus', () => {
            this.elements.messageInput.parentElement.classList.add('focused');
        });
        
        this.elements.messageInput.addEventListener('blur', () => {
            this.elements.messageInput.parentElement.classList.remove('focused');
        });
        
        // Suggestion chips
        document.querySelectorAll('.suggestion-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                const message = chip.getAttribute('data-message');
                this.elements.messageInput.value = message;
                this.sendMessage();
            });
        });
        
        // Clear chat button
        this.elements.clearChat.addEventListener('click', () => {
            this.clearChat();
        });
        
        // Analytics button
        this.elements.showAnalytics.addEventListener('click', () => {
            this.showAnalytics();
        });
        
        // Close analytics modal
        this.elements.closeAnalytics.addEventListener('click', () => {
            this.hideAnalytics();
        });
        
        // Close modal on backdrop click
        this.elements.analyticsModal.addEventListener('click', (e) => {
            if (e.target === this.elements.analyticsModal) {
                this.hideAnalytics();
            }
        });
        
        // Close toast notifications
        document.querySelectorAll('.close-toast').forEach(button => {
            button.addEventListener('click', (e) => {
                const toast = e.target.closest('.toast');
                this.hideToast(toast);
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals
            if (e.key === 'Escape') {
                this.hideAnalytics();
            }
            
            // Ctrl/Cmd + K to focus input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.elements.messageInput.focus();
            }
        });
    }
    
    sendMessage() {
        const message = this.elements.messageInput.value.trim();
        
        if (!message) {
            this.showError('Please enter a message');
            return;
        }
        
        if (!this.isConnected) {
            this.showError('Not connected to server. Please wait...');
            return;
        }
        
        // Clear input
        this.elements.messageInput.value = '';
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Send message via WebSocket
        this.socket.emit('message', {
            message: message,
            session_id: this.sessionId,
            user_id: this.userId
        });
        
        // Disable send button temporarily
        this.elements.sendButton.disabled = true;
        
        // Auto-enable after 2 seconds
        setTimeout(() => {
            this.elements.sendButton.disabled = false;
        }, 2000);
    }
    
    handleBotResponse(data) {
        this.hideTypingIndicator();
        
        if (data.bot_response) {
            this.addMessage(data.bot_response, 'bot', {
                intent: data.intent,
                confidence: data.confidence,
                entities: data.entities,
                sentiment: data.sentiment
            });
        }
        
        // Re-enable send button
        this.elements.sendButton.disabled = false;
    }
    
    addMessage(content, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = `${sender}-avatar`;
        avatar.innerHTML = sender === 'bot' ? '<i class=\"fas fa-robot\"></i>' : '<i class=\"fas fa-user\"></i>';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        
        // Add metadata for bot messages
        if (sender === 'bot' && metadata.intent) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-metadata';
            metaDiv.innerHTML = `
                <small style=\"opacity: 0.7; font-size: 0.75rem; margin-top: 0.5rem; display: block;\">
                    Intent: ${metadata.intent} (${Math.round(metadata.confidence * 100)}% confidence)
                </small>
            `;
            bubble.appendChild(metaDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Save to local storage
        this.saveChatHistory();
    }
    
    showTypingIndicator() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.elements.typingIndicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }
    
    hideTypingIndicator() {
        if (this.isTyping) {
            this.isTyping = false;
            this.elements.typingIndicator.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }
    
    updateConnectionStatus(message, status) {
        this.elements.connectionStatus.innerHTML = `
            <i class=\"fas fa-wifi\"></i>
            <span>${message}</span>
        `;
        this.elements.connectionStatus.className = `connection-status ${status}`;
        
        // Auto-hide after 3 seconds if connected
        if (status === 'connected') {
            setTimeout(() => {
                this.elements.connectionStatus.style.opacity = '0.7';
            }, 3000);
        }
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Remove all messages except welcome message
            const messages = this.elements.chatMessages.querySelectorAll('.message');
            messages.forEach(message => message.remove());
            
            // Clear local storage
            localStorage.removeItem(`chat_history_${this.sessionId}`);
            
            this.showSuccess('Chat history cleared');
        }
    }
    
    async showAnalytics() {
        this.elements.analyticsModal.style.display = 'flex';
        this.elements.analyticsContent.innerHTML = `
            <div class=\"loading\">
                <i class=\"fas fa-spinner fa-spin\"></i>
                Loading analytics...
            </div>
        `;
        
        try {
            const response = await fetch(`/api/analytics?user_id=${this.userId}`);
            const data = await response.json();
            
            if (response.ok) {
                this.renderAnalytics(data);
            } else {
                throw new Error(data.error || 'Failed to load analytics');
            }
        } catch (error) {
            console.error('Analytics error:', error);
            this.elements.analyticsContent.innerHTML = `
                <div class=\"error\">
                    <i class=\"fas fa-exclamation-triangle\"></i>
                    Failed to load analytics: ${error.message}
                </div>
            `;
        }
    }
    
    renderAnalytics(data) {
        const intentItems = Object.entries(data.intent_distribution || {})
            .map(([intent, count]) => `
                <li class=\"intent-item\">
                    <span class=\"intent-name\">${intent.replace('_', ' ')}</span>
                    <span class=\"intent-count\">${count}</span>
                </li>
            `).join('');
        
        this.elements.analyticsContent.innerHTML = `
            <div class=\"analytics-grid\">
                <div class=\"analytics-card\">
                    <h3>Total Conversations</h3>
                    <p class=\"value\">${data.total_conversations || 0}</p>
                </div>
                <div class=\"analytics-card\">
                    <h3>Total Messages</h3>
                    <p class=\"value\">${data.total_messages || 0}</p>
                </div>
                <div class=\"analytics-card\">
                    <h3>Avg Confidence</h3>
                    <p class=\"value\">${Math.round((data.average_confidence || 0) * 100)}%</p>
                </div>
            </div>
            
            <h3 style=\"margin-bottom: 1rem; color: #1e293b;\">Intent Distribution</h3>
            ${intentItems ? `<ul class=\"intent-list\">${intentItems}</ul>` : '<p>No intent data available</p>'}
        `;
    }
    
    hideAnalytics() {
        this.elements.analyticsModal.style.display = 'none';
    }
    
    showError(message) {
        this.elements.errorMessage.textContent = message;
        this.showToast(this.elements.errorToast);
    }
    
    showSuccess(message) {
        this.elements.successMessage.textContent = message;
        this.showToast(this.elements.successToast);
    }
    
    showToast(toast) {
        toast.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideToast(toast);
        }, 5000);
    }
    
    hideToast(toast) {
        toast.style.display = 'none';
    }
    
    saveChatHistory() {
        try {
            const messages = Array.from(this.elements.chatMessages.querySelectorAll('.message')).map(msg => {
                const isUser = msg.classList.contains('user');
                const content = msg.querySelector('.message-bubble').textContent;
                return {
                    sender: isUser ? 'user' : 'bot',
                    content: content,
                    timestamp: Date.now()
                };
            });
            
            localStorage.setItem(`chat_history_${this.sessionId}`, JSON.stringify(messages));
        } catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }
    
    loadChatHistory() {
        try {
            const history = localStorage.getItem(`chat_history_${this.sessionId}`);
            if (history) {
                const messages = JSON.parse(history);
                messages.forEach(msg => {
                    if (msg.sender !== 'welcome') { // Skip welcome message
                        this.addMessage(msg.content, msg.sender);
                    }
                });
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }
    
    // Utility method for API calls
    async apiCall(endpoint, options = {}) {
        try {
            const response = await fetch(endpoint, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API call failed:', error);
            throw error;
        }
    }
    
    // Method to send message via REST API (fallback)
    async sendMessageREST(message) {
        try {
            const data = await this.apiCall('/api/chat', {
                method: 'POST',
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    user_id: this.userId
                })
            });
            
            this.addMessage(data.bot_response, 'bot', {
                intent: data.intent,
                confidence: data.confidence,
                entities: data.entities,
                sentiment: data.sentiment
            });
            
        } catch (error) {
            this.showError('Failed to send message: ' + error.message);
        }
    }
}

// Utility functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if Socket.IO is loaded
    if (typeof io === 'undefined') {
        console.error('Socket.IO not loaded. Falling back to REST API.');
        // Could implement REST-only fallback here
        return;
    }
    
    // Initialize the chatbot application
    window.chatbot = new ChatbotApp();
    
    // Add some helpful console messages
    console.log('🤖 ProductivityBot initialized successfully!');
    console.log('💡 Tip: Use Ctrl+K (Cmd+K on Mac) to focus the input field');
    console.log('💡 Tip: Press Escape to close modals');
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.chatbot) {
        if (document.hidden) {
            console.log('Page hidden - maintaining connection');
        } else {
            console.log('Page visible - checking connection');
            if (!window.chatbot.isConnected) {
                window.chatbot.initializeSocket();
            }
        }
    }
});

// Handle online/offline events
window.addEventListener('online', () => {
    if (window.chatbot && !window.chatbot.isConnected) {
        console.log('Back online - reconnecting...');
        window.chatbot.initializeSocket();
    }
});

window.addEventListener('offline', () => {
    console.log('Gone offline - connection will be restored when back online');
});

// Export for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatbotApp;
}

