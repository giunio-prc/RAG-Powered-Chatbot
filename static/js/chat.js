// Chat functionality for streaming responses

class ChatManager {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.chatForm = document.getElementById('chat-form');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.clearChatButton = document.getElementById('clear-chat');

        this.isStreaming = false;
        this.currentStreamingMessage = null;
        this.abortController = null;
        this.storageKey = 'rag-chatbot-history';

        this.initializeEventListeners();
        setTimeout(() => this.loadChatHistory(), 100);
    }

    initializeEventListeners() {
        // Chat form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Clear chat button
        this.clearChatButton.addEventListener('click', () => {
            this.clearChat();
        });

        // Example question buttons
        document.querySelectorAll('.example-question').forEach(button => {
            button.addEventListener('click', () => {
                const question = button.dataset.question;
                this.messageInput.value = question;
                this.sendMessage();
            });
        });

        // Auto-resize textarea and Enter key handling
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Set welcome time
        const welcomeTime = document.getElementById('welcome-time');
        if (welcomeTime) {
            welcomeTime.textContent = this.formatTime(new Date());
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Clear input and disable form
        this.messageInput.value = '';
        this.setStreamingState(true);

        try {
            // Start streaming response
            await this.streamResponse(message);
        } catch (error) {
            handleError(error, 'Failed to get response');
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'assistant');
        } finally {
            this.setStreamingState(false);
        }
    }

    async streamResponse(question) {
        try {
            // Create new AbortController for this request
            this.abortController = new AbortController();

            const response = await fetch('/query-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(question),
                signal: this.abortController.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Create assistant message container
            const messageElement = this.createMessageElement('', 'assistant');
            const contentElement = messageElement.querySelector('.message-content');
            this.currentStreamingMessage = contentElement;

            // Read the stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                accumulatedText += chunk;

                // Update the message content
                contentElement.innerHTML = this.formatMessageContent(accumulatedText);

                // Scroll to bottom
                this.scrollToBottom();
            }

            // Save chat history after streaming is complete
            setTimeout(() => this.saveChatHistory(), 100);

        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Request was aborted');
                // Don't throw abort errors as they are intentional
                return;
            }
            console.error('Streaming error:', error);
            throw error;
        }
    }

    addMessage(content, sender) {
        const messageElement = this.createMessageElement(content, sender);
        this.scrollToBottom();
        // Delay saving to ensure DOM is fully updated
        setTimeout(() => this.saveChatHistory(), 100);
        return messageElement;
    }

    createMessageElement(content, sender) {
        const messageDiv = document.createElement('div');
        const isUser = sender === 'user';

        if (isUser) {
            messageDiv.className = 'flex justify-end mb-4';
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3 max-w-xs lg:max-w-md">
                    <div class="flex-1 bg-primary-600 text-white rounded-lg p-4 shadow-sm">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-medium text-primary-100">You</span>
                            <span class="text-xs text-primary-200">${this.formatTime(new Date())}</span>
                        </div>
                        <div class="message-content leading-relaxed">${this.formatMessageContent(content)}</div>
                    </div>
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            `;
        } else {
            messageDiv.className = 'flex items-start space-x-3 mb-4';
            messageDiv.innerHTML = `
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                </div>
                <div class="flex-1 bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-primary-600">AI Assistant</span>
                        <span class="text-xs text-gray-500">${this.formatTime(new Date())}</span>
                    </div>
                    <div class="message-content text-gray-800 leading-relaxed">${this.formatMessageContent(content)}</div>
                </div>
            `;
        }

        this.chatMessages.querySelector('.p-4.space-y-4').appendChild(messageDiv);
        return messageDiv;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatMessageContent(content) {
        if (!content) return '';

        // First escape all HTML special characters to prevent XSS
        let escaped = this.escapeHtml(content);

        // Convert line breaks to HTML
        let formatted = escaped.replace(/\n/g, '<br>');

        // Apply markdown-like formatting on the escaped text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

        return formatted;
    }

    setStreamingState(isStreaming) {
        this.isStreaming = isStreaming;
        this.sendButton.disabled = isStreaming;
        this.messageInput.disabled = isStreaming;
        this.clearChatButton.disabled = isStreaming;

        // Disable example question buttons during streaming
        document.querySelectorAll('.example-question').forEach(button => {
            button.disabled = isStreaming;
        });

        if (isStreaming) {
            this.loadingIndicator.classList.remove('hidden');
            this.sendButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="sr-only">Sending...</span>
            `;
        } else {
            this.loadingIndicator.classList.add('hidden');
            this.sendButton.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                <span class="sr-only">Send message</span>
            `;
            this.currentStreamingMessage = null;
            // Reset AbortController when streaming stops
            this.abortController = null;
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    clearChat() {
        // Abort any ongoing streaming request
        if (this.abortController && this.isStreaming) {
            this.abortController.abort();
            this.setStreamingState(false);
        }

        // Clear all messages except the welcome message
        const messagesContainer = this.chatMessages.querySelector('.p-4.space-y-4');
        const messages = messagesContainer.children;
        // Keep only the first message (welcome message)
        for (let i = messages.length - 1; i > 0; i--) {
            messages[i].remove();
        }

        // Clear stored chat history
        this.clearChatHistory();

        toast.show('Chat cleared successfully', 'success');
    }

    saveChatHistory() {
        const messagesContainer = this.chatMessages.querySelector('.p-4.space-y-4');
        const messages = Array.from(messagesContainer.children);

        // Skip the welcome message (first child) and only save user/assistant messages
        const chatHistory = messages.slice(1).map(messageDiv => {
            const isUser = messageDiv.classList.contains('justify-end');
            const contentElement = messageDiv.querySelector('.message-content');
            const timeElement = messageDiv.querySelector('.text-xs');

            return {
                content: contentElement ? contentElement.innerHTML : '',
                sender: isUser ? 'user' : 'assistant',
                timestamp: timeElement ? timeElement.textContent : this.formatTime(new Date())
            };
        });

        localStorage.setItem(this.storageKey, JSON.stringify(chatHistory));
    }

    loadChatHistory() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (!stored) return;

            const chatHistory = JSON.parse(stored);
            console.log('Loading chat history:', chatHistory.length, 'messages');
            const messagesContainer = this.chatMessages.querySelector('.p-4.space-y-4');

            // Restore each message
            chatHistory.forEach(message => {
                const messageElement = this.createStoredMessageElement(message);
                messagesContainer.appendChild(messageElement);
            });

            this.scrollToBottom();
        } catch (error) {
            console.error('Failed to load chat history:', error);
            // Clear corrupted data
            localStorage.removeItem(this.storageKey);
        }
    }

    createStoredMessageElement(messageData) {
        const messageDiv = document.createElement('div');
        const isUser = messageData.sender === 'user';

        if (isUser) {
            messageDiv.className = 'flex justify-end mb-4';
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-3 max-w-xs lg:max-w-md">
                    <div class="flex-1 bg-primary-600 text-white rounded-lg p-4 shadow-sm">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-medium text-primary-100">You</span>
                            <span class="text-xs text-primary-200">${messageData.timestamp}</span>
                        </div>
                        <div class="message-content leading-relaxed">${messageData.content}</div>
                    </div>
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            `;
        } else {
            messageDiv.className = 'flex items-start space-x-3 mb-4';
            messageDiv.innerHTML = `
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                </div>
                <div class="flex-1 bg-white rounded-lg p-4 shadow-sm border border-gray-200">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-primary-600">AI Assistant</span>
                        <span class="text-xs text-gray-500">${messageData.timestamp}</span>
                    </div>
                    <div class="message-content text-gray-800 leading-relaxed">${messageData.content}</div>
                </div>
            `;
        }

        return messageDiv;
    }

    clearChatHistory() {
        localStorage.removeItem(this.storageKey);
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if chat elements exist before initializing ChatManager
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');

    // Only initialize ChatManager if essential chat elements are present
    if (chatMessages && chatForm && messageInput) {
        window.chatManager = new ChatManager();
    }
});
