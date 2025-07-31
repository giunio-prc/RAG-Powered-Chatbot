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

        this.initializeEventListeners();
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

        // Enter key handling
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
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
            const response = await fetch('/query-stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(question)
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

        } catch (error) {
            console.error('Streaming error:', error);
            throw error;
        }
    }

    addMessage(content, sender) {
        const messageElement = this.createMessageElement(content, sender);
        this.scrollToBottom();
        return messageElement;
    }

    createMessageElement(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;

        const isUser = sender === 'user';
        const icon = isUser ? 'fas fa-user' : 'fas fa-robot';
        const iconColor = isUser ? 'text-blue-600' : 'text-blue-600';
        const senderName = isUser ? 'You' : 'AI Assistant';

        messageDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="${icon} ${iconColor} mr-3 mt-1"></i>
                <div class="flex-1">
                    <strong class="${iconColor}">${senderName}</strong>
                    <div class="message-content mt-1">${this.formatMessageContent(content)}</div>
                    <div class="text-xs text-gray-500 mt-2">${utils.formatDate(new Date())}</div>
                </div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        return messageDiv;
    }

    formatMessageContent(content) {
        if (!content) return '';

        // Convert line breaks to HTML
        let formatted = content.replace(/\n/g, '<br>');

        // Simple markdown-like formatting
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

        return formatted;
    }

    setStreamingState(isStreaming) {
        this.isStreaming = isStreaming;
        this.sendButton.disabled = isStreaming;
        this.messageInput.disabled = isStreaming;

        if (isStreaming) {
            this.loadingIndicator.classList.remove('d-none');
            this.sendButton.innerHTML = '<div class="spinner mr-2"></div>Sending...';
        } else {
            this.loadingIndicator.classList.add('d-none');
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Send';
            this.currentStreamingMessage = null;
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    clearChat() {
        // Keep only the initial welcome message
        const messages = this.chatMessages.querySelectorAll('.message');
        for (let i = 1; i < messages.length; i++) {
            messages[i].remove();
        }

        toast.show('Chat cleared successfully', 'success');
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatManager = new ChatManager();
});
