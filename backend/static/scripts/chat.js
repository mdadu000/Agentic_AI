// The import path is now correct
import ApiService from "./apiService.js";

const AgentName = "agent";
let activeSessionId = "";

document.addEventListener("DOMContentLoaded", () => {
  initChat();
});

…  }
});

// Form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  input.value = "";
  await sendMessage(text, currentFile);
});