import os
import uvicorn
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.service import Service
from repos.repo import Repo
from routers import restaurants, auth
from constants import DB_NAME
from ai.ai_service import ai_service_instance

repo = Repo(DB_NAME)
service = Service(repo)

app = FastAPI(
    title="EasyDine Backend (Groq Powered)",
    description="Direct Groq API integration without agent frameworks",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Chat API ---
class NewMessagePart(BaseModel):
    text: Optional[str] = None
    inlineData: Optional[Any] = None

class NewMessage(BaseModel):
    role: str = "user"
    parts: List[NewMessagePart] = []

class RunSSERequest(BaseModel):
    appName: Optional[str] = "agent"
    newMessage: Optional[NewMessage] = None
    sessionId: Optional[str] = None
    streaming: Optional[bool] = True
    userId: Optional[str] = "user"

# --- Session & Chat Endpoints ---

@app.post("/apps/{app_name}/users/{user_id}/sessions")
async def create_session(app_name: str, user_id: str):
    """Creates a new chat session."""
    session = ai_service_instance.create_session()
    return session

@app.get("/apps/{app_name}/users/{user_id}/sessions")
async def list_sessions(app_name: str, user_id: str):
    """Lists active chat sessions."""
    return ai_service_instance.list_sessions()

@app.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def get_session(app_name: str, user_id: str, session_id: str):
    """Retrieves session events and history."""
    session = ai_service_instance.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def delete_session(app_name: str, user_id: str, session_id: str):
    """Deletes a chat session."""
    deleted = ai_service_instance.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}

@app.post("/run_sse")
async def run_sse(req: RunSSERequest):
    """Streaming chat endpoint using direct Groq API completions."""
    session_id = req.sessionId or ai_service_instance.create_session()["id"]
    
    # Extract text content from message parts
    text_content = ""
    if req.newMessage and req.newMessage.parts:
        for part in req.newMessage.parts:
            if part.text:
                text_content += part.text + " "
    text_content = text_content.strip()

    if not text_content:
        text_content = "Hello"

    return StreamingResponse(
        ai_service_instance.run_sse(session_id=session_id, user_message=text_content),
        media_type="text/event-stream"
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)