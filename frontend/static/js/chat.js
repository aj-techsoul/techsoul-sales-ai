/* ==========================================
   TechSoul AI
   chat.js
   Handles chat messages only
========================================== */

const chatBox = document.getElementById("chat-box");

/* ==========================================
   ADD BOT MESSAGE
========================================== */

function addBotMessage(message) {

    const bubble = document.createElement("div");

    bubble.className = "bot-message";

    bubble.innerHTML = message;

    chatBox.appendChild(bubble);

    scrollChat();

}

/* ==========================================
   ADD USER MESSAGE
========================================== */

function addUserMessage(message) {

    const bubble = document.createElement("div");

    bubble.className = "user-message";

    bubble.textContent = message;

    chatBox.appendChild(bubble);

    scrollChat();

}

/* ==========================================
   SHOW TYPING INDICATOR
========================================== */

function showTyping() {

    const typing = document.getElementById("typing-indicator");

    typing.style.display = "flex";

    scrollChat();

}

/* ==========================================
   HIDE TYPING INDICATOR
========================================== */

function hideTyping() {

    const typing = document.getElementById("typing-indicator");

    typing.style.display = "none";

}

/* ==========================================
   AUTO SCROLL
========================================== */

function scrollChat() {

    chatBox.scrollTop = chatBox.scrollHeight;

}

/* ==========================================
   BOT REPLY WITH DELAY
========================================== */

function botReply(message, delay = 700) {

    showTyping();

    setTimeout(() => {

        hideTyping();

        addBotMessage(message);

    }, delay);

}

/* ==========================================
   CLEAR CHAT
========================================== */

function clearChat() {

    chatBox.innerHTML = "";

}

/* ==========================================
   INITIAL MESSAGE
========================================== */

function startConversation() {
    clearChat();
    botReply(`
        <h3>👋 Welcome to TechSoul AI</h3>
        <p>
            I'm your AI Business Consultant.
        </p>
        <p>
            Let's build your perfect software solution.
        </p>
        <p>
            <strong>What is your name?</strong>
        </p>
    `);
}

/* ==========================================
   START WHEN PAGE LOADS
========================================== */

window.addEventListener("load", () => {

    startConversation();

});