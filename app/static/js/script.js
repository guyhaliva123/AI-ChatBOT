const conversation = document.getElementById("conversation");
const textarea = document.getElementById("user_input");
const form = document.getElementById("chatForm");

// Auto-expand textarea and handle enter key
textarea.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = this.scrollHeight + "px";
});

// Handle enter key
textarea.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Add click handler for send button
document
  .querySelector('button[value="Chat"]')
  .addEventListener("click", function (e) {
    e.preventDefault();
    sendMessage();
  });

function sendMessage() {
  const message = textarea.value.trim();
  if (message) {
    // Show user message immediately
    const userDiv = document.createElement("div");
    userDiv.className = "message message-user";
    userDiv.textContent = message;
    conversation.appendChild(userDiv);
    conversation.scrollTop = conversation.scrollHeight;

    // Add typing indicator before bot response
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "typing-indicator message message-assistant";
    typingIndicator.innerHTML = `
              <span></span>
              <span></span>
              <span></span>
          `;
    conversation.appendChild(typingIndicator);
    conversation.scrollTop = conversation.scrollHeight;

    // Create form data
    const formData = new FormData();
    formData.append("user_input", message);
    formData.append("action", "Chat");

    // Clear textarea
    textarea.value = "";
    textarea.style.height = "auto";

    // Send to server
    fetch("/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error:", data.error);
          return;
        }

        // Remove typing indicator
        typingIndicator.remove();

        // Add bot response
        const botDiv = document.createElement("div");
        botDiv.className = "message message-assistant";

        // Create text container and format the text
        const textContainer = document.createElement("div");
        textContainer.className = "message-text";

        // Format the text: handle newlines and bold text
        const formattedText = data.response
          .split("\n")
          .map((line) => {
            // Replace **text** with <strong>text</strong>
            return line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
          })
          .join("<br>");

        // Set the formatted HTML
        textContainer.innerHTML = formattedText;

        botDiv.appendChild(textContainer);

        // Create copy button
        const copyButton = document.createElement("button");
        copyButton.className = "copy-button";
        copyButton.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          `;

        // Add copy functionality
        copyButton.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          try {
            // Create temporary textarea
            const tempTextArea = document.createElement("textarea");
            tempTextArea.value = data.response;
            document.body.appendChild(tempTextArea);

            // Select and copy the text
            tempTextArea.select();
            document.execCommand("copy");

            // Remove temporary textarea
            document.body.removeChild(tempTextArea);

            // Show success message
            const toast = document.createElement("div");
            toast.className = "toast-message";
            toast.textContent = "הועתק בהצלחה!";
            document.body.appendChild(toast);

            // Change button icon to checkmark
            copyButton.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="green" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `;

            // Remove toast after animation
            setTimeout(() => {
              toast.remove();
            }, 1000);

            // Reset button icon
            setTimeout(() => {
              copyButton.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
            `;
            }, 1500);
          } catch (err) {
            console.error("Failed to copy text:", err);

            // Show error message if copying fails
            const toast = document.createElement("div");
            toast.className = "toast-message";
            toast.style.backgroundColor = "#f44336";
            toast.textContent = "שגיאה בהעתקה";
            document.body.appendChild(toast);

            setTimeout(() => {
              toast.remove();
            }, 1000);
          }
        };

        botDiv.appendChild(copyButton);
        conversation.appendChild(botDiv);
        conversation.scrollTop = conversation.scrollHeight;
      })
      .catch((error) => {
        console.error("Error:", error);
        // Remove typing indicator on error
        typingIndicator.remove();
      });
  }
}

// Initial scroll to bottom
conversation.scrollTop = conversation.scrollHeight;
