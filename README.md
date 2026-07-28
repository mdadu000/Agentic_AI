# EasyDine AI

## 📘 Project Overview
**EasyDine** is a conversational AI-driven web application for discovering restaurants, viewing menus, exploring discounts, and booking table reservations. Powered directly by the **Groq API** using `llama-3.3-70b-versatile`, EasyDine communicates seamlessly with LLM completions and tool execution without any heavy agent frameworks or Google dependencies.

---

## 🛠️ Architecture & Tech Stack

- **Frontend**: HTML5, CSS3 (Modern Glassmorphic Design System, Plus Jakarta Sans & Outfit Fonts), Vanilla JavaScript.
- **Backend**: FastAPI (Python), `groq` official SDK, SQLite (`restaurant.db`).
- **AI Integration**: Direct Groq API completions (`llama-3.3-70b-versatile`) with native function tool schemas.

---

## 🚀 Steps to Start the Backend App

1. **Navigate to the backend directory**  
   ```bash
   cd backend
   ```

2. **Install the required dependencies**  
   Install all necessary Python packages:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Groq API Key**
   - Visit [Groq Console](https://console.groq.com/) and create a free account.
   - Go to API Keys and click **Create API Key**.
   - Copy your generated key string (`gsk_...`).

4. **Configure Environment Variables**
   - Create or edit the `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

5. **Run the backend server**  
   Start the FastAPI backend with:  
   ```bash
   python main.py
   ```
   The backend server will run at `http://127.0.0.1:8080`.

---

## 🌐 Steps to Start the Frontend App

1. **Configure Backend URL (Optional)**  
   - Open `frontend/services/apiService.js`.  
   - Verify `baseURL` points to `http://127.0.0.1:8080`.

2. **Open Frontend in Web Browser**  
   - Open `frontend/index.html` directly in your browser or run with Live Server.
   - Navigate to the **AI Assistant** page (`frontend/pages/chat.html`) to interact with the Groq AI model.