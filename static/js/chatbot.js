// Initialize chatbot
const chatWindow = document.getElementById('chatWindow');
const chatInput = document.getElementById('chatInput');

// Handle user messages
function handleUserMessage(message) {
    const response = "You said: " + message; // Simple echo response
    displayMessage(response);
}

// Display chatbot message
function displayMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
}

// Event listener for chat input
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const message = chatInput.value.trim();
        if (message) {
            handleUserMessage(message);
            chatInput.value = ''; // Clear input
        }
    }
}); 