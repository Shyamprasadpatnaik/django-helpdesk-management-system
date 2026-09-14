/**
 * JK Paper Mill - AI Troubleshooting Assistant Frontend
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-message-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const messagesBox = document.getElementById('chat-messages-container');

    if (chatInput && sendBtn && messagesBox) {
        sendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Quick prompt chips
        document.querySelectorAll('.prompt-chip').forEach(chip => {
            chip.addEventListener('click', function() {
                chatInput.value = this.textContent.trim();
                sendMessage();
            });
        });
    }

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Append User Message Bubble
        appendMessage('user', text);
        chatInput.value = '';

        // 2. Show Typing Indicator
        const typingId = appendTypingIndicator();
        messagesBox.scrollTop = messagesBox.scrollHeight;

        // 3. Send to API
        fetch('/chatbot/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            removeTypingIndicator(typingId);
            appendMessage('assistant', data.reply, data.suggested_dept, data.suggested_category);
            messagesBox.scrollTop = messagesBox.scrollHeight;
        })
        .catch(err => {
            removeTypingIndicator(typingId);
            appendMessage('assistant', "AI assistant is temporarily unavailable. You can still create a support ticket directly.");
            messagesBox.scrollTop = messagesBox.scrollHeight;
        });
    }

    function appendMessage(role, content, dept, cat) {
        const row = document.createElement('div');
        row.className = `chat-msg-row ${role === 'user' ? 'msg-user' : 'msg-bot'}`;

        let innerHtml = `
            <div class="chat-bubble ${role === 'user' ? 'bubble-user' : 'bubble-bot'}">
                <div class="msg-content">${formatText(content)}</div>
        `;

        if (role === 'assistant' && (dept || cat)) {
            innerHtml += `
                <div class="chat-actions mt-2 pt-2 border-top">
                    <span class="badge badge-info mb-2">Recommended: ${dept || 'Maintenance'} Department</span>
                    <br>
                    <a href="/tickets/create/?dept=${encodeURIComponent(dept || '')}" class="btn btn-sm btn-primary">
                        <i class="bi bi-ticket-perforated"></i> Create Ticket with this Context
                    </a>
                </div>
            `;
        }

        innerHtml += `</div>`;
        row.innerHTML = innerHtml;
        messagesBox.appendChild(row);
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const row = document.createElement('div');
        row.id = id;
        row.className = 'chat-msg-row msg-bot';
        row.innerHTML = `
            <div class="chat-bubble bubble-bot typing-bubble">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
        `;
        messagesBox.appendChild(row);
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function formatText(text) {
        // Simple safe formatter for line breaks and bold
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }
});
