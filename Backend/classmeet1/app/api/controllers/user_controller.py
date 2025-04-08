from fastapi import Depends, HTTPException
from pydantic import BaseModel
from app.dao.user_dao import UserDAO
from app.utils.auth import verify_jwt_token  # Đảm bảo import

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

async def get_user_info(token: str = Depends(verify_jwt_token)):
    dao = UserDAO()
    user = dao.find_by_id(token["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def update_user_info(update_data: UserUpdate, token: str = Depends(verify_jwt_token)):
    dao = UserDAO()
    update_dict = update_data.dict(exclude_unset=True)
    dao.update(token["sub"], update_dict)
    return await get_user_info(token)