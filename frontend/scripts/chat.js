import ApiService from "../services/apiService.js";
const AgentName = "agent";
let activeSessionId = "";

document.addEventListener("DOMContentLoaded", () => {
  initChat();
});

function initChat() {
  const newSessionButton = document.getElementById("new-session");
  if (newSessionButton) {
    newSessionButton.addEventListener("click", createSession);
  }
  listSessions();
}

// DOM elements
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const fileInput = document.getElementById("file-input");
const sessionsListWrapper = document.getElementById("sessions-list");

function listSessions() {
  if (!sessionsListWrapper) return; // Not on chat page
  ApiService.get(`/apps/${AgentName}/users/user/sessions`)
    .then((sessions) => {
      if (sessions && sessions.length) {
        activeSessionId = sessions[0].id;
        sessionsListWrapper.innerHTML = ""; // Clear list
        for (let i = 0; i < sessions.length; i++) {
          createSessionElement(sessions[i].id);
        }
        // Automatically load the first session
        updateActiveSession(activeSessionId);
      } else {
        createSession(); // If no sessions, create one
      }
    })
    .catch((error) => console.error(error));
}

function createSessionElement(id) {
  const li = document.createElement("li");
  li.setAttribute("id", `id-${id}`);
  li.setAttribute("class", "session-item");
  
  const spanEl = document.createElement("span");
  spanEl.innerHTML = id;
  li.appendChild(spanEl);
  
  const deleteIcon = document.createElement("i");
  deleteIcon.setAttribute("class", "fa fa-trash delete-session");
  deleteIcon.onclick = (event) => deleteSession(event, id);
  li.appendChild(deleteIcon);
  
  if (activeSessionId === id) {
    li.classList.add("active");
  }
  
  li.onclick = () => updateActiveSession(id);
  sessionsListWrapper.appendChild(li);
}

function createSession() {
  ApiService.post(`/apps/${AgentName}/users/user/sessions`)
    .then((session) => {
      activeSessionId = session.id;
      listSessions(); // Refresh the whole list to set active state
    })
    .catch((error) => console.error(error));
}

function deleteSession(event, id) {
  event.stopPropagation();
  ApiService.delete(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then(() => {
      const session = document.getElementById(`id-${id}`);
      const wasActive = session.classList.contains("active");
      session.parentNode.removeChild(session);
      
      if (wasActive) {
        const firstSession = document.querySelector(".session-item");
        if (firstSession) {
            firstSession.classList.add("active");
            activeSessionId = firstSession.getAttribute("id").replace('id-','');
            updateActiveSession(activeSessionId);
        } else {
            createSession(); // Create a new one if all are deleted
        }
      }
    })
    .catch((error) => console.error(error));
}

function updateActiveSession(id) {
  ApiService.get(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then((sessionResponse) => {
      const existingSessions =
        sessionsListWrapper.querySelectorAll(".session-item");
      if (existingSessions.length) {
        for (let j = 0; j < existingSessions.length; j++) {
          existingSessions[j].classList.remove("active");
        }
      }
      const listEl = document.getElementById(`id-${id}`);
      if (listEl) listEl.classList.add("active");
      
      activeSessionId = id;
      messagesEl.innerHTML = "";
      renderEvents(sessionResponse.events);
    })
    .catch((error) => console.error(error));
}

function renderEvents(events) {
  if (!events) return;
  for (let i = 0; i < events.length; i++) {
    if (events[i].content) {
      appendMessage(events[i].content, events[i].content.role);
    }
  }
}

// Helpers
function appendMessage(content, who = "model") {
  const el = document.createElement("div");
  if (content.parts) {
    for (let i = 0; i < content.parts.length; i++) {
      const part = content.parts[i];
      if (part.functionResponse) {
        el.className = `message model function`;
        el.innerHTML = `<i class="fa fa-check"></i> ${part.functionResponse.name}`;
      } else {
        el.className = `message ${who}`;
        if (part.text) {
          // Use marked.parse if marked is loaded
          if (typeof marked !== 'undefined') {
            el.innerHTML = marked.parse(part.text);
          } else {
            el.innerText = part.text;
          }
        }
        if (part.functionCall) {
          el.classList.add("function");
          el.innerHTML = `<i class="fa fa-bolt"></i> ${part.functionCall.name}`;
        }
        if (part.inlineData) {
          const mediaEl = createMediaElement(part.inlineData);
          if (mediaEl) {
            el.appendChild(mediaEl);
          }
        }
      }
    }
  }
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}

function createMediaElement({ data, mimeType, displayName }) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-media";
  // The backend ADK service uses URL-safe base64, so we must reverse it
  const encrpytedData = data.replace(/_/g, "/").replace(/-/g, "+");
  
  if (mimeType.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = `data:${mimeType};base64,${encrpytedData}`;
    img.alt = displayName || "User upload";
    img.loading = "lazy";
    wrapper.appendChild(img);
  } else {
    // For non-image files, show a download link
    const link = document.createElement("a");
    link.href = `data:${mimeType};base64,${encrpytedData}`;
    link.download = displayName || "file";
    link.innerHTML = `<i class="fa fa-download"></i> ${displayName || "Download File"}`;
    wrapper.appendChild(link);
  }

  return wrapper;
}

function setSending(isSending) {
  if (sendBtn) sendBtn.disabled = isSending;
  if (input) input.disabled = isSending;
}

// File handling
let currentFile = null;
const filePreview = document.getElementById("file-preview"); 

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Extract the base64 data from the DataURL
      const base64Data = reader.result.split(",")[1];
      resolve({
        data: base64Data,
        displayName: file.name,
        mimeType: file.type,
      });
    };
    reader.onerror = (error) => reject(error);
  });
}

function showFilePreview(file) {
  if (!filePreview) return;
  filePreview.innerHTML = "";
  if (!file) return;

  const wrapper = document.createElement("div");
  wrapper.className = "preview-wrapper";

  if (file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.className = "message-media preview";
    const reader = new FileReader();
    reader.onload = (e) => (img.src = e.target.result);
    reader.readAsDataURL(file);
    wrapper.appendChild(img);
  } else {
    const fileInfo = document.createElement("div");
    fileInfo.className = "file-info";
    fileInfo.innerHTML = `<i class="fa fa-file"></i> ${file.name}`;
    wrapper.appendChild(fileInfo);
  }

  const removeBtn = document.createElement("button");
  removeBtn.className = "remove-preview";
  removeBtn.innerHTML = '<i class="fa fa-times"></i>';
  removeBtn.onclick = clearFilePreview;
  wrapper.appendChild(removeBtn);

  filePreview.appendChild(wrapper);
}

function clearFilePreview() {
  if (filePreview) filePreview.innerHTML = "";
  currentFile = null;
  if (fileInput) fileInput.value = "";
}

async function sendMessage(text, attachedFile = null) {
  if (!text && !attachedFile) return;

  // Show user's message
  setSending(true);
  const parts = [];

  if (text) {
    parts.push({ text });
  }

  if (attachedFile) {
    const base64Data = await fileToBase64(attachedFile);
    parts.push({ inlineData: base64Data });
  }

  appendMessage({ parts }, "user");
  clearFilePreview();

  const payload = {
    appName: AgentName,
    newMessage: { role: "user", parts },
    sessionId: activeSessionId,
    stateDelta: null,
    streaming: true, // Set to true for streaming
    userId: "user",
  };

  try {
    await ApiService.postWithStream(
      "/run_sse", // Use the streaming endpoint
      payload, 
      async (chunk) => {
        if (chunk && typeof chunk === "object" && chunk.content) {
            appendMessage(chunk.content, "model");
            messagesEl.scrollTop = messagesEl.scrollHeight;
        } else if (chunk && chunk.sessionId) {
            activeSessionId = chunk.sessionId;
        }
      }
    );
  } catch (err) {
    console.error("Chat error:", err);
    appendMessage({ parts: [{ text: `**Error:** ${err.message || "Could not connect to agent."}` }] }, "model");
  } finally {
    setSending(false);
  }
}

// File input handler
if (fileInput) {
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      currentFile = file;
      showFilePreview(file);
    }
  });
}

// Form submit
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    input.value = "";
    await sendMessage(text, currentFile);
  });
}