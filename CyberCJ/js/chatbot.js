document.addEventListener('DOMContentLoaded', () => {
    const chatbotWidget = document.getElementById('chatbot-widget');
    const chatbotToggle = document.getElementById('chatbot-toggle');
    const chatbotClose = document.getElementById('chatbot-close');
    const messagesContainer = document.getElementById('chatbot-messages');
    const inputField = document.getElementById('chatbot-input');
    const sendButton = document.getElementById('chatbot-send');
    const moduleSelector = document.getElementById('module-selector');
    const newTopicBtn = document.getElementById('new-topic-btn');

    // --- API Endpoints ---
    const API_URL = '/chat_multi_agent'; // CJ-Mentor API endpoint (relative URL for deployment)
    const FEEDBACK_URL = '/feedback'; // Feedback endpoint (relative URL for deployment)

    // --- Global Variables ---
    let conversationId = generateConversationId();
    let messageCounter = 0;

    // --- Utility Functions ---
    function generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function formatMarkdownToHtml(text) {
        let html = text
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code snippets
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Bullet points
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            // Convert lists
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            // Numbered lists
            .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
            // Line breaks
            .replace(/\n/g, '<br>');

        return html;
    }

    // --- Toggle Chatbot Widget ---
    function toggleWidget(forceOpen = null) {
        const isOpen = chatbotWidget.classList.contains('open');
        if (forceOpen === true || (!isOpen && forceOpen === null)) {
            chatbotWidget.classList.add('open');
            chatbotToggle.classList.add('hidden');
            inputField.focus();
        } else if (forceOpen === false || (isOpen && forceOpen === null)) {
            chatbotWidget.classList.remove('open');
            chatbotToggle.classList.remove('hidden');
        }
    }

    chatbotToggle.addEventListener('click', () => toggleWidget(true));
    chatbotClose.addEventListener('click', () => toggleWidget(false));

    // --- Message Management ---
    function addMessage(text, type, messageId = null) {
        messageCounter++;
        const actualMessageId = messageId || `msg_${messageCounter}`;

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        messageDiv.setAttribute('data-message-id', actualMessageId);
        messageDiv.style.position = 'relative';

        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');

        // Apply Markdown formatting only to bot/system messages
        if (type === 'bot-message' || type === 'system-message') {
            contentDiv.innerHTML = formatMarkdownToHtml(text);
        } else {
            contentDiv.textContent = text;
        }

        messageDiv.appendChild(contentDiv);

        // Add feedback buttons for bot messages
        if (type === 'bot-message') {
            const feedbackContainer = document.createElement('div');
            feedbackContainer.classList.add('feedback-container');

            const thumbsUp = document.createElement('button');
            thumbsUp.classList.add('feedback-btn');
            thumbsUp.innerHTML = '👍';
            thumbsUp.title = 'Good response';
            thumbsUp.onclick = () => submitFeedback(actualMessageId, 'positive', text);

            const thumbsDown = document.createElement('button');
            thumbsDown.classList.add('feedback-btn');
            thumbsDown.innerHTML = '👎';
            thumbsDown.title = 'Poor response';
            thumbsDown.onclick = () => submitFeedback(actualMessageId, 'negative', text);

            feedbackContainer.appendChild(thumbsUp);
            feedbackContainer.appendChild(thumbsDown);
            messageDiv.appendChild(feedbackContainer);
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageDiv;
    }

    // --- Feedback System ---
    async function submitFeedback(messageId, rating, responseText) {
        try {
            const response = await fetch(FEEDBACK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_id: messageId,
                    conversation_id: conversationId,
                    rating: rating,
                    response_text: responseText,
                    timestamp: new Date().toISOString()
                }),
            });

            if (response.ok) {
                // Update button state
                const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
                if (messageDiv) {
                    const buttons = messageDiv.querySelectorAll('.feedback-btn');
                    buttons.forEach(btn => btn.classList.remove('active'));

                    const clickedButton = event.target;
                    clickedButton.classList.add('active');

                    // Add feedback status
                    let statusSpan = messageDiv.querySelector('.feedback-status');
                    if (!statusSpan) {
                        statusSpan = document.createElement('span');
                        statusSpan.classList.add('feedback-status');
                        messageDiv.appendChild(statusSpan);
                    }
                    statusSpan.textContent = rating === 'positive' ? '✓ Helpful' : '✓ Noted';
                }
            }
        } catch (error) {
            console.error('Feedback submission error:', error);
        }
    }

    // --- Typing Indicator ---
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing');
        typingDiv.textContent = 'CJ-Mentor is thinking...';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return typingDiv;
    }

    function removeTypingIndicator(typingDiv) {
        if (typingDiv && typingDiv.parentNode) {
            typingDiv.parentNode.removeChild(typingDiv);
        }
    }

    // --- Send Message to API ---
    async function sendMessage() {
        const question = inputField.value.trim();
        if (!question) return;

        addMessage(question, 'user-message');
        inputField.value = '';
        inputField.disabled = true;
        sendButton.disabled = true;

        const typingIndicator = showTypingIndicator();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: question,
                    conversation_id: conversationId
                }),
            });

            removeTypingIndicator(typingIndicator);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: "An unknown error occurred" }));
                console.error('API Error:', response.status, errorData);
                addMessage(errorData.error || `Error: ${response.statusText}`, 'bot-message error');
                return;
            }

            const data = await response.json();

            // Handle system messages if present
            if (data.system_message) {
                addMessage(data.system_message, 'system-message');
            }

            // Add the main response
            const responseMessageId = generateConversationId();
            addMessage(data.response, 'bot-message', responseMessageId);

        } catch (error) {
            removeTypingIndicator(typingIndicator);
            console.error('Fetch Error:', error);
            addMessage('Sorry, I encountered an error trying to connect. Please try again later.', 'bot-message error');
        } finally {
            inputField.disabled = false;
            sendButton.disabled = false;
            inputField.focus();
        }
    }

    // --- Event Listeners ---
    sendButton.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Module selector functionality
    moduleSelector.addEventListener('change', (event) => {
        const selectedModule = event.target.value;
        if (selectedModule) {
            const moduleMessages = {
                'introduction': 'I\'d like to learn about **Introduction to Cybersecurity**. Can you create a learning plan for this module?',
                'computer-security': 'I\'d like to learn about **Computer Security**. Can you create a learning plan for this module?',
                'internet-security': 'I\'d like to learn about **Internet Security**. Can you create a learning plan for this module?',
                'privacy': 'I\'d like to learn about **Privacy**. Can you create a learning plan for this module?'
            };

            if (moduleMessages[selectedModule]) {
                inputField.value = moduleMessages[selectedModule];
                sendMessage();
                event.target.value = ''; // Reset selector
            }
        }
    });

    // New topic button functionality
    newTopicBtn.addEventListener('click', () => {
        conversationId = generateConversationId(); // Start fresh conversation
        messagesContainer.innerHTML = ''; // Clear chat
        setTimeout(() => {
            addMessage('Great! Let\'s start a **new topic**. What cybersecurity concept would you like to explore today?', 'system-message');
        }, 100);
    });

    // --- Initialize ---
    // Add welcome message
    setTimeout(() => {
        addMessage('Hello! I\'m **CJ-Mentor**, your cybersecurity learning companion. I can help you understand cybersecurity concepts and create personalized learning plans. What would you like to learn about today?', 'bot-message');
    }, 500);
});