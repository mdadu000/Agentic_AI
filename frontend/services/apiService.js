// API Service configuration
const API_CONFIG = {
  baseURL: "http://127.0.0.1:8080",
  headers: {
    "Content-Type": "application/json",
  },
};

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    
    // FIX: Convert object errors to string so they are readable
    let errorMessage = error.message || `HTTP error! status: ${response.status}`;
    if (error.detail) {
        errorMessage = typeof error.detail === 'object' 
            ? JSON.stringify(error.detail) 
            : error.detail;
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

const buildURL = (endpoint) => {
  if (endpoint.startsWith('/')) endpoint = endpoint.substring(1);
  return `${API_CONFIG.baseURL}/${endpoint}`;
};

export { buildURL, API_CONFIG };

class ApiService {
  static async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${buildURL(endpoint)}${queryString ? `?${queryString}` : ""}`;
    const response = await fetch(url, { method: "GET", headers: API_CONFIG.headers });
    return handleResponse(response);
  }

  static async post(endpoint, data = {}) {
    const response = await fetch(buildURL(endpoint), {
      method: "POST",
      headers: API_CONFIG.headers,
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  }

  static async put(endpoint, data = {}) {
    const response = await fetch(buildURL(endpoint), {
      method: "PUT",
      headers: API_CONFIG.headers,
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  }

  static async delete(endpoint) {
    const response = await fetch(buildURL(endpoint), {
      method: "DELETE",
      headers: API_CONFIG.headers,
    });
    return handleResponse(response);
  }

  static async postWithStream(endpoint, data = {}, onChunk = null) {
    const response = await fetch(buildURL(endpoint), {
      method: "POST",
      headers: { ...API_CONFIG.headers, Accept: "text/event-stream" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
       const errText = await response.text();
       throw new Error(`Stream Error: ${response.status} - ${errText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop();

      for (const part of parts) {
          if (part.startsWith("data: ")) {
              try {
                  const jsonStr = part.substring(6).trim();
                  if (jsonStr !== "[DONE]") {
                      const jsonData = JSON.parse(jsonStr);
                      if (onChunk) await onChunk(jsonData);
                  }
              } catch (e) {
                  console.warn("Error parsing chunk", e);
              }
          }
      }
    }
    return { success: true };
  }
}

export default ApiService;