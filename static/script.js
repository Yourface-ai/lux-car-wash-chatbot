// static/script.js
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

const sendSound = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-modern-technology-select-3124.mp3");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage("You", message, "user");
  userInput.value = "";

  appendTypingEffect("Lux Assistant");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    removeTypingEffect();
    appendMessage("Lux Assistant", data.response, "bot");
  } catch (error) {
    removeTypingEffect();
    appendMessage("Lux Assistant", "Oops, something went wrong.", "bot");
  }
});

function appendMessage(sender, message, type) {
  const bubble = document.createElement("div");
  bubble.className = `message ${type}`;
  bubble.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(bubble);
  chatBox.scrollTop = chatBox.scrollHeight;
  sendSound.play();
}

function appendTypingEffect(sender) {
  const typing = document.createElement("div");
  typing.className = "message bot typing";
  typing.id = "typing";
  typing.innerHTML = `<strong>${sender}:</strong> <span class="dots"><span>.</span><span>.</span><span>.</span></span>`;
  chatBox.appendChild(typing);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTypingEffect() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}
