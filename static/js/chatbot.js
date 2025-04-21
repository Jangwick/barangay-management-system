const chatbot = {
    init() {
        this.addChatbotToDOM();
        this.attachEventListeners();
    },

    addChatbotToDOM() {
        const chatbotHtml = `
            <div id="chatbot" class="fixed bottom-4 right-4 z-[9999]">
                <button id="chatbot-toggle" class="bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700">
                    <i class="fas fa-comment-dots text-2xl"></i>
                </button>
                <div id="chat-window" class="hidden absolute bottom-16 right-0 w-96 bg-white rounded-lg shadow-xl">
                    <div class="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                        <h3 class="font-bold">System Assistant</h3>
                        <button id="chat-close" class="text-white hover:text-gray-200">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="chat-messages" class="p-4 h-96 overflow-y-auto"></div>
                    <div class="border-t p-4">
                        <div id="quick-actions" class="grid grid-cols-2 gap-2 mb-4">
                            <button class="quick-nav text-left px-3 py-2 text-sm rounded-lg border hover:bg-blue-50" data-action="residents">👥 Residents</button>
                            <button class="quick-nav text-left px-3 py-2 text-sm rounded-lg border hover:bg-blue-50" data-action="documents">📄 Documents</button>
                            <button class="quick-nav text-left px-3 py-2 text-sm rounded-lg border hover:bg-blue-50" data-action="officials">👔 Officials</button>
                            <button class="quick-nav text-left px-3 py-2 text-sm rounded-lg border hover:bg-blue-50" data-action="help">❓ Help</button>
                        </div>
                        <form id="chat-form" class="flex gap-2">
                            <input type="text" id="chat-input" class="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Type your question...">
                            <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', chatbotHtml);
    },

    attachEventListeners() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.getElementById('chat-close');
        const form = document.getElementById('chat-form');
        const quickNavs = document.querySelectorAll('.quick-nav');

        toggle?.addEventListener('click', () => this.toggleChat());
        close?.addEventListener('click', () => this.toggleChat());
        form?.addEventListener('submit', (e) => this.handleSubmit(e));
        quickNavs?.forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickNav(e.target.dataset.action));
        });
    },

    toggleChat() {
        const window = document.getElementById('chat-window');
        const isHidden = window.classList.contains('hidden');
        window.classList.toggle('hidden');
        
        if (isHidden && !this.welcomed) {
            this.addMessage('bot', 'Hello! How can I help you today? You can use the quick navigation buttons or type your question.');
            this.welcomed = true;
        }
    },

    async handleSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        input.value = '';

        try {
            const response = await this.sendMessage(message);
            this.addMessage('bot', response.message, response.links);
        } catch (error) {
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    },

    async handleQuickNav(action) {
        try {
            const response = await this.sendMessage(action);
            this.addMessage('bot', response.message, response.links);
        } catch (error) {
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    },

    addMessage(sender, message, links = []) {
        const messages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-4 ${sender === 'user' ? 'text-right' : ''}`;
        
        const bubble = document.createElement('div');
        bubble.className = `inline-block p-3 rounded-lg ${
            sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'
        }`;
        bubble.textContent = message;
        messageDiv.appendChild(bubble);

        if (links.length > 0) {
            const linksDiv = document.createElement('div');
            linksDiv.className = 'mt-2';
            links.forEach(link => {
                const a = document.createElement('a');
                a.href = link.url;
                a.className = 'text-blue-600 hover:underline block';
                a.textContent = link.text;
                linksDiv.appendChild(a);
            });
            messageDiv.appendChild(linksDiv);
        }

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    },

    async sendMessage(message) {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        return await response.json();
    }
};

document.addEventListener('DOMContentLoaded', () => chatbot.init());
