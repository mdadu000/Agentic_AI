import ApiService from "../services/apiService.js";

const AgentName = "agent";
let activeSessionId = "";

// --- SECURITY: GLOBAL DUPLICATE PREVENTION ---
window.LAST_MESSAGE_HASH = "";
window.LAST_MESSAGE_TIME = 0;

// --- VOICE SPEECH RECOGNITION ---
let recognition = null;
let isListening = false;

document.addEventListener("DOMContentLoaded", () => {
    initChat();
});

function initChat() {
    console.log("🛡️ Chat System Online");

    // 1. NUCLEAR RESET OF FORM
    const oldForm = document.getElementById("chat-form");
    if (oldForm) {
        const newForm = oldForm.cloneNode(true);
        oldForm.parentNode.replaceChild(newForm, oldForm);
        newForm.onsubmit = (e) => handleFormSubmit(e);
    }

    // 2. NUCLEAR RESET OF NEW SESSION BUTTON
    const oldBtn = document.getElementById("new-session");
    if (oldBtn) {
        const newBtn = oldBtn.cloneNode(true);
        oldBtn.parentNode.replaceChild(newBtn, oldBtn);
        newBtn.onclick = createSession;
    }

    // 3. NUCLEAR RESET OF FILE INPUT
    const oldInput = document.getElementById("file-input");
    if (oldInput) {
        const newInput = oldInput.cloneNode(true);
        oldInput.parentNode.replaceChild(newInput, oldInput);
        newInput.onchange = handleFileChange;
    }

    // 4. INIT VOICE RECOGNITION
    initVoiceRecognition();

    // 5. BIND ENTER KEY PRESS ON TEXTAREA TO SUBMIT FORM
    const msgInput = document.getElementById("message-input");
    if (msgInput) {
        msgInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleFormSubmit(e);
            }
        });
    }

    listSessions();
}

function initVoiceRecognition() {
    const micBtn = document.getElementById("mic-btn");
    const statusBadge = document.getElementById("voice-status");
    const inputField = document.getElementById("message-input");

    if (!micBtn) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.title = "Voice recognition not supported in this browser";
        micBtn.style.opacity = "0.4";
        micBtn.onclick = () => alert("Web Speech Recognition API is not supported in this browser. Please use Chrome, Edge, or Safari.");
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add("recording");
        if (statusBadge) statusBadge.classList.remove("hidden");
    };

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        if (inputField) {
            inputField.value = transcript;
        }
    };

    recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        stopVoiceRecognition();
    };

    recognition.onend = () => {
        stopVoiceRecognition();
    };

    micBtn.onclick = () => {
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (e) {
                console.error("Speech start error:", e);
            }
        }
    };
}

function stopVoiceRecognition() {
    isListening = false;
    const micBtn = document.getElementById("mic-btn");
    const statusBadge = document.getElementById("voice-status");
    if (micBtn) micBtn.classList.remove("recording");
    if (statusBadge) statusBadge.classList.add("hidden");
}

// --- HANDLERS ---

async function handleFormSubmit(e) {
    if (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        e.stopPropagation();
    }

    const input = document.getElementById("message-input");
    const fileInput = document.getElementById("file-input");
    const text = input.value.trim();
    const currentFile = fileInput ? fileInput.files[0] : null;

    if (!text && !currentFile) return;

    // Stop voice if listening
    if (isListening && recognition) recognition.stop();

    // --- NETWORK DEBOUNCER ---
    const currentHash = `${text}-${currentFile ? currentFile.name : 'nofile'}-${activeSessionId}`;
    const now = Date.now();

    if (window.LAST_MESSAGE_HASH === currentHash && (now - window.LAST_MESSAGE_TIME < 2000)) {
        return; 
    }

    window.LAST_MESSAGE_HASH = currentHash;
    window.LAST_MESSAGE_TIME = now;

    toggleInputState(false);

    try {
        input.value = "";
        if (fileInput) fileInput.value = "";
        const preview = document.getElementById("file-preview");
        if (preview) preview.innerHTML = "";

        await sendMessage(text, currentFile);
    } catch (err) {
        console.error("Chat Error:", err);
        appendMessage({ parts: [{ text: `**Error:** ${err.message}` }] }, "model");
    } finally {
        toggleInputState(true);
        setTimeout(() => {
            const field = document.getElementById("message-input");
            if (field) field.focus();
        }, 100);
    }
}

function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) showFilePreview(file);
}

// --- CORE MESSAGING ---

async function sendMessage(text, attachedFile = null) {
    let fullText = text;

    if (attachedFile) {
        if (attachedFile.type.startsWith("image/")) {
            fullText += `\n[Attached Image: ${attachedFile.name}]`;
        } else if (
            attachedFile.type.startsWith("text/") || 
            attachedFile.name.endsWith(".json") || 
            attachedFile.name.endsWith(".csv") || 
            attachedFile.name.endsWith(".txt") ||
            attachedFile.name.endsWith(".pdf")
        ) {
            try {
                const fileText = await attachedFile.text();
                fullText += `\n\n--- Attached Document (${attachedFile.name}) ---\n${fileText.substring(0, 2500)}`;
            } catch (e) {
                fullText += `\n[Attached File: ${attachedFile.name}]`;
            }
        }
    }

    const parts = [];
    if (fullText) parts.push({ text: fullText });

    if (attachedFile && attachedFile.type.startsWith("image/")) {
        const base64Data = await fileToBase64(attachedFile);
        parts.push({ inlineData: base64Data });
    }

    // 1. Show User Message
    appendMessage({ parts }, "user");

    const payload = {
        appName: AgentName,
        newMessage: { role: "user", parts },
        sessionId: activeSessionId,
        streaming: true,
        userId: "user",
    };

    const response = await fetch("http://127.0.0.1:8080/run_sse", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    
    // Stream State
    let currentBubble = null;
    let accumulatedText = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop(); 

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                const jsonStr = line.substring(6).trim();
                if (jsonStr === "[DONE]") continue;

                try {
                    const chunk = JSON.parse(jsonStr);
                    if (chunk.sessionId) activeSessionId = chunk.sessionId;

                    if (chunk.content && chunk.content.parts) {
                        const part = chunk.content.parts[0];
                        
                        // CASE A: Tool Call (Function)
                        if (part.functionCall || part.functionResponse) {
                            if (!isLastElementDuplicateTool(part)) {
                                appendMessage(chunk.content, "model");
                            }
                            currentBubble = null; 
                            accumulatedText = ""; 
                        }
                        // CASE B: Text Streaming
                        else if (part.text) {
                            if (!currentBubble) {
                                const lastMsg = getLastModelMessageText();
                                const cleanNewText = part.text.trim();
                                const cleanLastText = lastMsg.trim();

                                if (cleanLastText.length > 0 && cleanLastText === cleanNewText) {
                                    continue;
                                }

                                currentBubble = appendMessage({ parts: [{ text: "" }] }, "model");
                                accumulatedText = ""; 
                            }
                            
                            if (currentBubble) {
                                accumulatedText += part.text;
                                if (typeof marked !== 'undefined') {
                                    currentBubble.innerHTML = marked.parse(accumulatedText);
                                } else {
                                    currentBubble.innerText = accumulatedText;
                                }
                                const messagesEl = document.getElementById("messages");
                                if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
                            }
                        }
                    }
                } catch (e) {
                    // Ignore parse errors
                }
            }
        }
    }
}

// --- UI HELPERS & DEDUPLICATION LOGIC ---

function getLastModelMessageText() {
    const messagesEl = document.getElementById("messages");
    if (!messagesEl) return "";
    
    const lastMsg = messagesEl.lastElementChild;
    if (lastMsg && lastMsg.classList.contains("model") && !lastMsg.classList.contains("function")) {
        return lastMsg.innerText;
    }
    return "";
}

function isLastElementDuplicateTool(newPart) {
    const messagesEl = document.getElementById("messages");
    if (!messagesEl || !messagesEl.lastElementChild) return false;
    
    const lastMsg = messagesEl.lastElementChild;
    const isModel = lastMsg.classList.contains('model');
    const isFunc = lastMsg.classList.contains('function');
    
    if (isModel && isFunc) {
        if (newPart.functionCall && lastMsg.innerText.includes(newPart.functionCall.name)) return true;
        if (newPart.functionResponse && lastMsg.innerText.includes(newPart.functionResponse.name)) return true;
    }
    return false;
}

function toggleInputState(enabled) {
    const btn = document.getElementById("send-btn");
    const inp = document.getElementById("message-input");
    if (btn) {
        btn.disabled = !enabled;
        btn.innerHTML = enabled ? '<i class="fa fa-paper-plane"></i>' : '<i class="fa fa-spinner fa-spin"></i>';
    }
    if (inp) inp.disabled = !enabled;
}

function appendMessage(content, who) {
    const messagesEl = document.getElementById("messages");
    if (!messagesEl) return null;

    if (who === 'model') {
        const lastMsg = messagesEl.lastElementChild;
        if (lastMsg && lastMsg.classList.contains('model')) {
            let newText = "";
            if (content.parts) {
                content.parts.forEach(p => { if(p.text) newText += p.text; });
            }
            
            if (newText.trim().length > 0 && lastMsg.innerText.trim() === newText.trim()) {
                return null;
            }
        }
    }

    const el = document.createElement("div");
    el.className = `message ${who}`;
    
    let hasContent = false;

    if (content.parts) {
        for (const part of content.parts) {
            if (part.functionResponse) {
                el.className = `message model function`;
                el.innerHTML = `<i class="fa fa-check"></i> Executed: ${part.functionResponse.name}`;
                hasContent = true;
            } else if (part.functionCall) {
                el.className = `message model function`;
                el.innerHTML = `<i class="fa fa-bolt"></i> Tool: ${part.functionCall.name}`;
                hasContent = true;
            } else if (part.text) {
                if (typeof marked !== 'undefined') {
                    el.innerHTML = marked.parse(part.text);
                } else {
                    el.innerText = part.text;
                }
                hasContent = true;
            } else if (part.inlineData) {
                const media = createMediaElement(part.inlineData);
                if (media) el.appendChild(media);
                hasContent = true;
            }
        }
    }

    if (hasContent || who === 'model') {
        messagesEl.appendChild(el);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return el;
    }
    return null;
}

function createMediaElement({ data, mimeType }) {
    const wrapper = document.createElement("div");
    wrapper.className = "message-media";
    const encrpytedData = data.replace(/_/g, "/").replace(/-/g, "+");
    if (mimeType.startsWith("image/")) {
        const img = document.createElement("img");
        img.src = `data:${mimeType};base64,${encrpytedData}`;
        img.style.maxWidth = "220px";
        img.style.borderRadius = "8px";
        wrapper.appendChild(img);
    } else {
        wrapper.innerHTML = `<i class="fa fa-file"></i> Document Attached`;
    }
    return wrapper;
}

async function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve({
            data: reader.result.split(",")[1],
            displayName: file.name,
            mimeType: file.type
        });
        reader.onerror = reject;
    });
}

function showFilePreview(file) {
    const preview = document.getElementById("file-preview");
    const icon = file.type.startsWith("image/") ? "fa-image" : "fa-file-lines";
    if (preview) {
        preview.innerHTML = `
            <div class="preview-wrapper">
                <i class="fa-solid ${icon}"></i> 
                <span>${file.name}</span>
                <button type="button" class="btn-clear-file" onclick="document.getElementById('file-input').value=''; document.getElementById('file-preview').innerHTML='';">&times;</button>
            </div>
        `;
    }
}

// --- SESSION MANAGEMENT ---

function listSessions() {
    const listEl = document.getElementById("sessions-list");
    if (!listEl) return;
    
    ApiService.get(`/apps/${AgentName}/users/user/sessions`)
        .then((sessions) => {
            listEl.innerHTML = "";
            if (sessions && sessions.length) {
                activeSessionId = sessions[0].id;
                sessions.forEach(s => createSessionElement(s.id));
                updateActiveSession(activeSessionId);
            } else {
                createSession();
            }
        }).catch(console.error);
}

function createSessionElement(id) {
    const listEl = document.getElementById("sessions-list");
    const li = document.createElement("li");
    li.id = `id-${id}`;
    li.className = "session-item";
    li.innerHTML = `<span>Session ${id.substring(0, 8)}...</span> <i class="fa fa-trash delete-session"></i>`;
    li.onclick = () => updateActiveSession(id);
    li.querySelector(".delete-session").onclick = (e) => deleteSession(e, id);
    listEl.appendChild(li);
}

function createSession() {
    ApiService.post(`/apps/${AgentName}/users/user/sessions`)
        .then(session => {
            activeSessionId = session.id;
            listSessions();
        });
}

function deleteSession(e, id) {
    e.stopPropagation();
    ApiService.delete(`/apps/${AgentName}/users/user/sessions/${id}`)
        .then(() => {
            const el = document.getElementById(`id-${id}`);
            if (el) el.remove();
            listSessions();
        });
}

function updateActiveSession(id) {
    activeSessionId = id;
    const listEl = document.getElementById("sessions-list");
    if (listEl) listEl.querySelectorAll(".session-item").forEach(el => el.classList.remove("active"));
    const activeEl = document.getElementById(`id-${id}`);
    if (activeEl) activeEl.classList.add("active");

    const messagesEl = document.getElementById("messages");
    if (messagesEl) messagesEl.innerHTML = "";
    
    window.LAST_MESSAGE_HASH = "";

    ApiService.get(`/apps/${AgentName}/users/user/sessions/${id}`)
        .then(res => {
            if (res.events) res.events.forEach(e => appendMessage(e.content, e.content.role));
        });
}