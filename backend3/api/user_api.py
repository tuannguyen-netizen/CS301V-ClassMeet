# api/user_api.py
from fastapi import APIRouter, Depends, HTTPException
from management.auth import get_current_user
from management.user_manager import get_user_profile

router = APIRouter()

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    return await get_user_profile(user_id)
