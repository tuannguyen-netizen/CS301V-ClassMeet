from fastapi import APIRouter, Depends, HTTPException
from dao.user.user_dao import UserDAO
from dao.user.object import User
from management.auth import get_current_user

router = APIRouter()
user_dao = UserDAO()

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user)):
    user = await user_dao.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()