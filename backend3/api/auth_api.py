# api/auth_api.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from management.auth_manager import register_user, login_user
from management.auth import get_current_user
from management.models import TokenResponse

logger = logging.getLogger(__name__)
router = APIRouter()

class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)

class UserLoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegistrationRequest):
    return await register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest):
    return await login_user(login_data)

@router.post("/logout")
async def logout(user_id: str = Depends(get_current_user)):
    return {"success": True, "message": "Successfully logged out"}
