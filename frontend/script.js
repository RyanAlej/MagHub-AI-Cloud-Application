// find the HTML element with ID askButton and store it in the variable askButton
// const = creating a variable
// askButton = variable name
// document = the JS object that represents the entire HTML webpage
// getElementById("askButton") = hey document, go find the element whose ID is askButton
const askButton = document.getElementById("askButton");

// store the question input element from HTML
const questionInput = document.getElementById("question");

// store the answer paragraph element from HTML, this is not the answer text
// answerParagraph is equal to <p id="answer"></p> from HTML
    // const answerParagraph = document.getElementById("answer");

const chatContainer = document.getElementById("chatContainer");

const inputBar = document.getElementById("inputBar");

const chatSessionsContainer = document.getElementById("chatSessionsContainer");

const sidebar = document.getElementById("sidebar");

const sidebarToggle = document.getElementById("sidebarToggle");

let currentChatId = null;

// new Set() creates a collection that stores unique chat IDs with unread AI responses
const unreadChatIds = new Set();

const newChatButton = document.getElementById("newChatButton");


const knowledgeBaseButton = document.getElementById("knowledgeBaseButton");

const closeKnowledgeBaseButton = document.getElementById("closeKnowledgeBaseButton");

const knowledgeBaseContainer = document.getElementById("knowledgeBaseContainer");

const settingsButton = document.getElementById("settingsButton");

const aboutButton = document.getElementById("aboutButton");


const contextMenu = document.getElementById("contextMenu");

const deleteChat = document.getElementById("deleteChat");

const renameChat = document.getElementById("renameChat");


const chatDrafts = {};

// when a link inside an AI message is clicked, open it in a new browser tab
// THIS DOES NOT decide what URL to use, it just creates the link of whatever the AI message supplied
chatContainer.addEventListener("click", function (event) {

    // event.target = the exact HTML element the user clicked
    // was the clicked element an <a> link located inside an .ai-message?
    if (event.target.matches(".ai-message a")) {

        // prevent the link from opening the current MagHub tab
        event.preventDefault();

        // open the link's URL in a new browser tab
        // event.target.href means get the URL from that link
        // this entire sequence means open that URL in a new tab, safely
        window.open(event.target.href, "_blank", "noopener, noreferrer");
    }
});

sidebarToggle.addEventListener("click", function () {

    sidebar.classList.toggle("collapsed");
    document.body.classList.toggle("sidebar-open");
});

document.addEventListener("click", function (event) {

    // does the sidebar currently have the collapsed class? 
    // ! flips the answer so if true it is now false

    // its asking... is the sidebar open?
    if (!sidebar.classList.contains("collapsed")

    // does the sidebar contain the element that was clicked? 
    && !sidebar.contains(event.target)

    // the click was NOT on the toggle button
    && !sidebarToggle.contains(event.target) 

    // click is NOT inside the context menu
    && !contextMenu.contains(event.target)

    // ENTIRE SEQUENCE FROM ABOVE
        // IF... the sidebar is open
        // AND the click was outisde the sidebar
        // AND the click was not on the toggle button
        // then close the sidebar
) {
    sidebar.classList.add("collapsed");
    console.log("Closing sidebar");
    document.body.classList.remove("sidebar-open");
}});


function addConversation(question, answer) {

    // += for integers adds them together. for strings, it adds the word to the end
    // ` backtick is the f-string from python 
    // marked.parse creates a <p> so p cant be in another p, line move down and placed in div
    // class="conversation-card" means div belongs to this group. each conv. in loop gets that label
    chatContainer.innerHTML += `

        <div class="user-row">
            <div class="user-message">
                ${question}
            </div>
        </div>

        <div class="ai-row">
            <div class="ai-message">
                ${marked.parse(answer)}
            </div>
        </div>
        `;

    chatContainer.scrollTop = chatContainer.scrollHeight;
}


function addChatSession(chatId, title) {

    unreadNotificationsClass = unreadChatIds.has(chatId) ? " unread" : "";

    chatSessionsContainer.innerHTML += `
    
        <div class="chat-session" data-chat-id="${chatId}">
            <span class="chat-title">${title}</span>
            <span class="unread-dot${unreadNotificationsClass}"></span>
        </div>
    `;

    // checks whether this chat ID is stored as unread
    // .has() means check whether that chatId currently exists inside the set
    if (unreadChatIds.has(chatId)) {

        // finds the unread dot inside this specific chat session
        const unreadDot = document.querySelector(

            `.chat-session[data-chat-id="${chatId}"] .unread-dot`
        );

        // makes the stored unread notification visible again
        unreadDot.classList.add("unread");
    }
}


// passes in "Unable to reach the server." from addSystemMessage
function addSystemMessage(message) {

    chatContainer.innerHTML += `

    <div class="system-message">
        ${message}
    </div>
    `;

}


async function loadChatSessions() {

    const response = await fetch("/chat-sessions");

    const chatSessions = await response.json();

    chatSessionsContainer.innerHTML = "";

    for (const chat of chatSessions) {

        addChatSession(
            
            chat.id,
            chat.title
        );
    }

    // .chat-session is corresponding to the CLASS in the template literal
    const chatButtons = document.querySelectorAll(".chat-session");

    for (const button of chatButtons) {

        button.addEventListener("click", async function () {

            // saves the unfinished draft from the chat we're leaving
            if (currentChatId !== null) {

                // chatDrafts[currentChatId] = the saved draft that belongs to current chat (chatDrafts[7] for example)
                // questionInput.value = whatever text is currently typed in the input box
                // this line is saying save what's currently typed into the chat's draft
                chatDrafts[currentChatId] = questionInput.value;
            }

            askButton.textContent = "Ask";
            askButton.disabled = false;

            document.querySelectorAll(".chat-session").forEach(function(chat) {
                chat.classList.remove("active");
            });

            button.classList.add("active");

            // finds the unread notification dot inside the chat that was just opened
            const unreadDot = button.querySelector(".unread-dot");

            // removes the unread class so the notification dot becomes hidden again
            unreadDot.classList.remove("unread");

            // data-chat-id corresponds to the template literal as HTML attribute NOT CLASS
            currentChatId = parseInt(button.getAttribute("data-chat-id"));

            // restores this chat's unfinished draft, or shows an empty input if it has none
            // questionInput.value = the text that should appear in the input box
            // chatDrafts[currentChatId] = the saved draft for the chat you just opened
            // || "" = if there isn't a saved draft, use an empty input instead
                // || means OR and "" means clear whatever is there to blank
            questionInput.value = chatDrafts[currentChatId] || "";

            // removes the opened chat ID from the Set because its response has now been seen
            unreadChatIds.delete(currentChatId);

            const response = await fetch(

            `/chat-sessions/${currentChatId}`
        );

        const conversations = await response.json();

        chatContainer.innerHTML = "";

        for (const conversation of conversations) {

            addConversation(

                conversation.question,
                conversation.answer
            );
        }
    });

    button.addEventListener("contextmenu", async function (event) {

        event.preventDefault();
        event.stopPropagation();

        const chatId = parseInt(button.getAttribute("data-chat-id"));

        const menu = document.getElementById("contextMenu");

        // remembers that context menu is currently at chat #7
        menu.dataset.chatId = chatId;

        // move the menu where the mouse already is
        menu.style.left = event.pageX + "px";
        menu.style.top = event.pageY + "px";

        menu.style.display = "block"; 
    });

}}

// flow goes = no current chat --> blank screen --> no old chat highlighted
newChatButton.addEventListener("click", function() {

    if (currentChatId !== null) {

        chatDrafts[currentChatId] = questionInput.value;
    }

    currentChatId = null;

    questionInput.value = "";
    askButton.textContent = "Ask";
    askButton.disabled = false;

    chatContainer.innerHTML = `

        <div class="new-chat-message">
            <h2>New Chat</h2>
            <p>Ask a question to start a conversation</p>
        </div>
    `;

    document.querySelectorAll(".chat-session").forEach(function(button) {

        button.classList.remove("active");
    });

    // physically collapses the sidebar
    sidebar.classList.add("collapsed");

    // moves your header/input bar back to their normal positions
    document.body.classList.remove("sidebar-open");

    questionInput.focus();
});


knowledgeBaseContainer.style.display = "none";

knowledgeBaseButton.addEventListener("click", function() {

    chatContainer.style.display = "none";

    inputBar.style.display = "none";

    sidebarToggle.style.display ="none";

    sidebar.classList.add("collapsed");
    document.body.classList.remove("sidebar-open")

    header.classList.add("knowledge-base-header");

    // block means SHOW the knowledge base when clicking the button
    knowledgeBaseContainer.style.display = "block";
});

closeKnowledgeBaseButton.addEventListener("click", function() {

    // when clicing the X close button, now the knowledge base container closes and shows none
    knowledgeBaseContainer.style.display = "none";

    chatContainer.style.display = "";

    inputBar.style.display = "";

    sidebarToggle.style.display ="";

    sidebar.classList.remove("collapsed");

    header.classList.remove("knowledge-base-header");
});


async function loadHistory() {

    const response = await fetch("/history");

    // json() extract JSON body from response object
    const data = await response.json();

    // innerHTML = everything between the opening and closing HTML tags
    chatContainer.innerHTML = "";

    for (const conversation of data) {

        addConversation(
            conversation.question,
            conversation.answer
        );
    }
}

questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {
        askButton.click();
    }
});


// run this code when the Ask button is clicked
askButton.addEventListener("click", async function () {

    // stores which chat this request started from so changing chats later doesn't change response belongs
    // basically copying the value at this moment 
    let requestChatId = currentChatId;

    try {

        // .value gets the current text entered inside the question input element
        const question = questionInput.value;

        // remembers whether this request originally start from the new chat screen
        const requestStartedAsNewChat = requestChatId === null;

        // .trim() removes the whitespace from the beginning/end so blank spaces don't count as question
        if (question.trim() === "") {

            addSystemMessage("Please enter a valid question.");
            return;
        }

        askButton.disabled = true;


        // .queryselector() searches the HTML and returns the first element with this class
        // stores the new-chat-message HTML element OR null if it is not on the page
            // const newChatMessage = document.querySelector(".new-chat-message");


        // checks whether newChatMessage actually contains an HTML element
        // if the new chat placeholder exists, run the code inside the braces
        if (currentChatId === null) {

            // = "" replaces everything currently inside the chatContainer
            chatContainer.innerHTML = "";
        }

        // .insertAdjacentHTML("beforeend",...) adds new HTML to the end of chatContainer without
            // replacing its existing contents
        chatContainer.insertAdjacentHTML("beforeend", `
        
            <div class="user-row">
                <div class="user-message">
                    ${question}
                </div>
            </div>
        `);

        const newestUserMessage = chatContainer.lastElementChild;

        newestUserMessage.scrollIntoView({

            behavior: "smooth",
            block: "start"
        });

        if (currentChatId !== null) {

            delete chatDrafts[currentChatId];
        }

        questionInput.value = "";

        // ai-row & loading-row uses existing ai-row so the loading animation appears where AI response is
            // space between them means this HTML element has two separate CSS classes
        // ai-loading is the actual loading indicator container
        // loading-spinner & loading-text are empty HTML elements to put animated visual in place
        chatContainer.insertAdjacentHTML("beforeend", `

            <div class="ai-row loading-row">
                <div class="ai-loading">
                    <span class="loading-spinner"></span>
                    <span class="loading-text">Thinking...</span>
                </div>
            </div>
        `);

        // store the loading row so it can be removed when the AI starts responding
        const loadingRow = chatContainer.querySelector(".loading-row");

        const loadingMessages = [

            "Thinking...",
            "Analyzing...",
            "Working through it...",
            "Preparing response...",
            "Almost done..."
        ]

        // grabs the loading text so JS can change what it says
        const loadingMessagesCycle = loadingRow.querySelector(".loading-text");

        let loadingMessageIndex = 0;

        // changes the loading message every 2 seconds
        // setInterval(function, time)
        const loadingMessageInterval = setInterval(() => {

            // the function
            loadingMessageIndex += 1;

            // loops back to the first mesage after reaching the end of the array
            loadingMessageIndex = loadingMessageIndex % loadingMessages.length;

            // changes the text to the current loading messages
            loadingMessagesCycle.textContent = loadingMessages[loadingMessageIndex];

        // the time
        }, 2000);
        
        // send the question to the FastAPI backend
        // fetch is like requests.post()
        // send something to this URL which is the FastAPI endpoint
        // send the request... and wait here until the server replies
        const response = await fetch("/ask", {

            // send a POST request by sending data
            method: "POST",

            // headers tells FastAPI we're sending JSON, otherwise FastAPI wouldn't know how to interpret it
            // content type = what type of data is in the body
            // then it would be the body is formatted as JSON
            // application/json is an HTTP standard not JS
            headers: {
                "Content-Type": "application/json"
            },

            // convert the JavaScript object into JSON
            // JSON.stringify means to convert this JS object (question: question) into JSON before sending
            // the body of this HTTP request is this JSON
            body: JSON.stringify({
                question: question,
                chat_id: requestChatId
            })
        });

        // this is placed here so not using data from a failed request and stops it before
        // check whether the server responded with an error status
        if (!response.ok) {

            // manually create an error so the catch block handles it
            // something went wrong... stop executing this try block and jump to catch
            throw new Error("Server returned an error.");
        }

        const responseChatId = response.headers.get("X-Chat-Id");

        // get the RAG sources that python sent in the X-Sources response header
        const sourcesHeader = response.headers.get("X-Sources");

        // convert the JSON source text into a JS array
        const retrievedSources = sourcesHeader ? JSON.parse(sourcesHeader) : [];

        console.log("Chat ID header from backend:", responseChatId);

        // converts the returned chat ID from text into a number and stores it as request's perm chat ID
        requestChatId = parseInt(responseChatId);

        // only change the currently viewed chat ID if the user has not switched to another chat
        // are we currently starting from new chat, where there wasn't an ID yet?
        // OR
        // are we still looking at the same chat this request belongs to?
        // IF SO then safe to set currentChatId to the returned ID
        if (
            (requestStartedAsNewChat && currentChatId === null) ||
            currentChatId === requestChatId
        ) {

            currentChatId = requestChatId;
        }

        // .body is the response data stream
        // .getReader() is built-in JS method that creates an object used to read data from stream
        const reader = response.body.getReader();

        // TextDecoder is a built-in JS class that converts bytes into readable text
        const decoder = new TextDecoder();

        // creates an empty AI message element that the streamed text will fill
        // insertAdjacentHTML = adds new HTML at a specific position without replacing existing HTML
        // beforeend = inserts the new HTML at the end, but still inside the selected HTML
        chatContainer.insertAdjacentHTML("beforeend", `
        
            <div class="ai-row">
                <div class="ai-message streaming-message"></div>
            </div>
        `);

        // querySelector finds the first HTML element with the streaming-message class
        const aiMessage = document.querySelector(".streaming-message");

        // stores all text chunks together as one complete answer
        let fullAnswer = "";

        // tracks whether the first AI text chunk has arrived
        let firstChunkReceived = false;

        while (true) {

            // .read() gets the next chunk from the stream
            // value = the chunk of bytes
            // done = boolean saying whether the stream ended
            // waits for the next stream chunk, then stores bytes in VALUE and finished status in DONE
            const { value, done } = await reader.read();

            // ends the loop when the stream is finished
            if (done) {
                break;
            }

            // .decode() converts the byte chunk into text
            // stream: true = tells TextDecoder that more chunks are still coming
            const textChunk = decoder.decode(value, { stream: true });

            if (!firstChunkReceived) {

                // stops the loading message cycle when the AI starts responding
                clearInterval(loadingMessageInterval);

                // remove the temporary loading message because the AI response is ready to stream
                loadingRow.remove();
                firstChunkReceived = true;

            }

            fullAnswer += textChunk;

            // marked.parse converts the accumulated Markdown answer into HTML
            aiMessage.innerHTML = marked.parse(fullAnswer);
        };

    // .classList.remove() removes the temporary streaming-message class after AI response finishes
    aiMessage.classList.remove("streaming-message");

    // only add a sources section if RAG actually returned sources
    if (retrievedSources.length > 0) {

        // add the Sources heading underneath the AI's answer
        aiMessage.insertAdjacentHTML("beforeend", "<hr><strong id='sourcesLabel'>Sources:</strong>");

        const displayedSources = new Set();

        // go through each source python sent to JS
        for (const source of retrievedSources) {

            if (displayedSources.has(source.url)) {

                continue;
            }

            displayedSources.add(source.url);

            if (source.name.includes("Virginia Code")) {

                aiMessage.insertAdjacentHTML(

                    "beforeend",
                    `<div>Virginia Code - <a class="source-link" href="${source.url}">§ ${source.name.split("§ ")[1]}</a></div>`
                );
            }

            else {

                const sourceDisplayName = source.name
                    .replace(".pdf", "")
                    .replace("chapter", "Chapter ");

                aiMessage.insertAdjacentHTML(

                    "beforeend",
                    `<div>Magistrate Field Guide - <a class="source-link" href="${source.url}">${sourceDisplayName}</a></div>`
                );
            }
        }
    }

    // if the AI response finished in a chat that the user is no longer viewing
    if (currentChatId !== requestChatId) {

        // stores this chat ID in the Set so the app remembers it has an unread AI response
        unreadChatIds.add(requestChatId);
    }

    await loadChatSessions();

    }


    catch (errorObject) {

        // this comes from throw error and shows the message of the errorObject 
        if (errorObject.message === "Server returned an error.") {

            addSystemMessage("The server encountered an error. Please try again.");
        }

        else {

            addSystemMessage("Unable to reach the server.");
        }

        // error prints text with icon and in red in the dev console
        console.error(errorObject);
    }

    finally {

        // only reset the controls if the user is still viewing
            // the same chat that started this request
        if (currentChatId === requestChatId) {
            // change the ask button back 
            askButton.textContent = "Ask";
            askButton.disabled = false;
        };
    }

});

loadChatSessions();

document.addEventListener("click", function(event) {

    if(!contextMenu.contains(event.target)) {

        contextMenu.style.display = "none";
    }

});


deleteChat.addEventListener("click", async function (event) {

    event.stopPropagation();

    const chatId = parseInt(contextMenu.dataset.chatId);

    await fetch (`/chat-sessions/${chatId}`, {

        method: "DELETE"
    });

    contextMenu.style.display = "none";

    await loadChatSessions();
});

renameChat.addEventListener("click", async function() {

    const chatId = parseInt(contextMenu.dataset.chatId);

    const newTitle = prompt("Enter a new chat title: ");

    await fetch (`/chat-sessions/${chatId}`, {

        method: "PATCH",

        headers: {

            "Content-Type": "application/json"

            },

            // stringify converts JS object to JSON
            body: JSON.stringify({
                title: newTitle
        })
    });

    loadChatSessions();
})
