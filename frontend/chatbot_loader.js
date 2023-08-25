document.addEventListener('DOMContentLoaded', function() {

    var chatbotHTML = `
        <div id="chatbot-container">
        <iframe style="border: none;"  id="chatbot-widget" src="chatbot.html"></iframe>
        </div>
        <button id="expand-button" class="cool-button">Expand</button>
        <button id="chatbot-button" class="cool-button">Open Chatbot</button>
    `;

    // Create CSS
    var chatbotCSS = `
    body {
            margin: 0;
            padding: 0;
        }
        #chatbot-container {
            position: fixed;
            bottom: 75px;
            right: 0px;
            width: 330px;
            height: 400px;
            z-index: -1000;
            opacity: 0;
            transform: translateY(100px);
            transition: width 0.5s, height 0.5s, opacity 0.5s, transform 0.5s;
        }
        #chatbot-container.open {
            opacity: 1;
            transform: translateY(0);
            z-index: 1000;
        }
        #chatbot-container.full {
            width: 100%;
            height: 85%;
            z-index: 1000;
        }
        #chatbot-widget {
            width: 100%;
            height: 100%;
        }
        #expand-button {
            position: fixed;
            bottom: 10px;
            right: 215px;
            z-index: -1001;
            display: none;
            max-width: 130px;
        }

        #chatbot-container.full #expand-button {
            top: 40px;
            right: 40px;
            z-index: -1001;
        }
        #chatbot-button {
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 1001;
            max-width: 180px;
        }

        .cool-button{
        background-color: #3b548a; 
        border: none;
        color: white; /* White text */
        padding: 15px 32px; /* Some padding */
        text-align: center; /* Centered text */
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        transition-duration: 0.5s; /* 0.5 second transition */
        cursor: pointer; /* Add a hand cursor on hover over the button */
        border-radius: 4px; /* Rounded corners */
        box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23); /* Add shadows for 3D look */

        }

        iframe {
    background-color: transparent;
}
    `;

    // Append CSS to the head
    var styleElement = document.createElement("style");
    styleElement.innerHTML = chatbotCSS;
    document.head.appendChild(styleElement);

    // Append HTML to the body
    var container = document.createElement("div");
    container.innerHTML = chatbotHTML;
    document.body.appendChild(container);

    // JavaScript code
    try{
    var pageChatButton = document.getElementById("page-chat-button");
    pageChatButton.addEventListener("click", function() {
        chatbotContainer.classList.toggle("open");
        if (chatbotContainer.classList.contains("open")) {
            chatbotButton.innerHTML = "Close Chatbot";
            expandButton.style.display = "block";
        } else {
            chatbotButton.innerHTML = "Open Chatbot";
            expandButton.style.display = "none";
        }
    });
    } catch (e) {}
    var chatbotContainer = document.getElementById("chatbot-container");
        var chatbotButton = document.getElementById("chatbot-button");
        var expandButton = document.getElementById("expand-button");
        chatbotButton.addEventListener("click", function() {
            chatbotContainer.classList.toggle("open");
            if (chatbotContainer.classList.contains("open")) {
                chatbotButton.innerHTML = "Close Chatbot";
                chatbotButton.style.zIndex = "1000";
                expandButton.style.display = "block";
                expandButton.style.zIndex = "1000";
            } else {
                chatbotButton.innerHTML = "Open Chatbot";
                expandButton.style.display = "none";
                expandButton.style.zIndex = "-1000";
            }
        });
    
        expandButton.addEventListener("click", function() {
            chatbotContainer.classList.toggle("full");
            if (chatbotContainer.classList.contains("full")) {
                expandButton.innerHTML = "Minimize";
            } else {
                expandButton.innerHTML = "Expand";

            }
        });

}, false);
