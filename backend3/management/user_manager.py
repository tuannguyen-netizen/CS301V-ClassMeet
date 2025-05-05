# management/user_manager.py
from fastapi import HTTPException
from dao.user_dao import UserDAO

user_dao = UserDAO()

async def get_user_profile(user_id: str):
    user = await user_dao.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()
