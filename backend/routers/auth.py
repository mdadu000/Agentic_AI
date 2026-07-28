from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "user"  # "user" or "admin"

# Mock database of users for quick login/signup verification
MOCK_USERS = {
    "admin@easydine.com": {
        "name": "System Administrator",
        "email": "admin@easydine.com",
        "password": "admin123",
        "role": "admin"
    },
    "user@easydine.com": {
        "name": "Demo User",
        "email": "user@easydine.com",
        "password": "user123",
        "role": "user"
    }
}

@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate user or admin"""
    email_clean = req.email.strip().lower()
    
    if email_clean in MOCK_USERS:
        stored_user = MOCK_USERS[email_clean]
        if stored_user["password"] == req.password:
            return {
                "message": "Login successful",
                "user": {
                    "name": stored_user["name"],
                    "email": stored_user["email"],
                    "role": stored_user["role"]
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid email or password")
    else:
        # Auto-create user for frictionless testing if valid email structure
        role = "admin" if "admin" in email_clean else "user"
        name = email_clean.split("@")[0].capitalize()
        MOCK_USERS[email_clean] = {
            "name": name,
            "email": email_clean,
            "password": req.password,
            "role": role
        }
        return {
            "message": "Login successful",
            "user": {
                "name": name,
                "email": email_clean,
                "role": role
            }
        }

@router.post("/signup")
async def signup(req: SignupRequest):
    """Register new user or admin"""
    email_clean = req.email.strip().lower()
    role = req.role if req.role in ("user", "admin") else "user"
    if "admin" in email_clean:
        role = "admin"

    MOCK_USERS[email_clean] = {
        "name": req.name,
        "email": email_clean,
        "password": req.password,
        "role": role
    }

    return {
        "message": "User registered successfully",
        "user": {
            "name": req.name,
            "email": email_clean,
            "role": role
        }
    }
