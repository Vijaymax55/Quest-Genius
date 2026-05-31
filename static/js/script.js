// script.js
document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is working!");


    // Increment the visitor count - MODIFIED SECTION
    const visitorCountKey = "visitorCount";
    let visitorCount = parseInt(localStorage.getItem(visitorCountKey)) || 0;
    visitorCount++; // Natural increment
    localStorage.setItem(visitorCountKey, visitorCount);
    document.getElementById("visitor-number").innerText = visitorCount.toLocaleString();

    // Display the current date and time in IST with a 12-hour format
    function updateDateTime() {
        const options = {
            timeZone: "Asia/Kolkata",
            hour12: true,
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        };
        const now = new Date();
        const dateTimeString = now.toLocaleDateString("en-IN", options);
        document.getElementById("date-time").innerText = dateTimeString;
    }

    setInterval(updateDateTime, 1000); // Update every second
    updateDateTime(); // Initial call to set the time immediately


// Chatbot Functionality
function sendQuestion() {
    const input = document.getElementById('chat-input');
    const chatBox = document.getElementById('chat-box');
    const question = input.value.trim();

    if (question) {
        addMessageToChatBox("You", question, chatBox);

        // Simulate an AI response (replace with actual API call for production)
        setTimeout(() => {
            addMessageToChatBox("Chatbot", "That's a great question! Here's something related...", chatBox);
        }, 1000);

        input.value = ''; // Clear the input after sending
    }
}

function checkEnter(event) {
    if (event.keyCode === 13) { // keyCode 13 is the Enter key
        sendQuestion();
    }
}

// Helper function to append messages to the chatbox
function addMessageToChatBox(sender, messageContent, chatBox) {
    const message = document.createElement('div');
    message.textContent = `${sender}: ${messageContent}`;
    chatBox.appendChild(message);
}



// Chatbot Send Message Functionality
function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message) {
        const chatBox = document.getElementById('chat-box');
        addMessageToChatBox("You", message, chatBox);

        // Simulated bot response
        setTimeout(() => {
            addMessageToChatBox("Bot", "Here's something related to your question...", chatBox);
        }, 1000);

        input.value = ''; // Clear the input field
    }
}
});
