let ws = null;
let currentSessionId = null;
let currentMessageDiv = null;

const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const sendBtn = document.getElementById('sendBtn');
const statusText = document.getElementById('statusText');
const statusDot = document.querySelector('.status-dot');

connectBtn.onclick = () => {
    currentSessionId = 'user_' + Math.random().toString(36).substring(2, 11);
    ws = new WebSocket(`ws://${window.location.host}/ws/session/${currentSessionId}`);

    statusText.textContent = "Connecting...";

    ws.onopen = () => {
        statusDot.className = 'status-dot connected';
        statusText.textContent = "Connected";

        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
        sendBtn.disabled = false;
        document.getElementById('chatContainer').style.display = 'block';

        addSystemMessage("Session started!");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'token') {
            if (!currentMessageDiv) {
                currentMessageDiv = document.createElement('div');
                currentMessageDiv.className = 'message message-ai';
                currentMessageDiv.innerHTML = '<div class="message-content"></div><div class="message-time">' + new Date().toLocaleTimeString() + '</div>';
                currentMessageDiv.dataset.raw = "";
                messagesDiv.appendChild(currentMessageDiv);
            }

            const contentDiv = currentMessageDiv.querySelector('.message-content');
            currentMessageDiv.dataset.raw += data.content;
            contentDiv.innerHTML = marked.parse(currentMessageDiv.dataset.raw);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        else if (data.type === 'complete') {
            currentMessageDiv = null;
        }
        else if (data.type === 'error') {
            addSystemMessage("Error: " + data.content);
        }
    };

    ws.onclose = () => {
        statusDot.className = 'status-dot offline';
        statusText.textContent = "Disconnected";
        connectBtn.disabled = false;
        disconnectBtn.disabled = true;
        sendBtn.disabled = true;
        addSystemMessage("Session ended. Summary generating...");
    };
};

disconnectBtn.onclick = () => {
    if (ws) ws.close();
};

sendBtn.onclick = () => {
    const text = messageInput.value.trim();
    if (!text) return;

    const div = document.createElement('div');
    div.className = 'message message-user';
    div.innerHTML = `<div class="message-content">${text}</div><div class="message-time">${new Date().toLocaleTimeString()}</div>`;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    ws.send(JSON.stringify({ type: 'message', content: text }));
    messageInput.value = '';
};

messageInput.onkeypress = (e) => {
    if (e.key === 'Enter') sendBtn.click();
};

function addSystemMessage(text) {
    const div = document.createElement('div');
    div.className = 'message message-system';
    div.textContent = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
