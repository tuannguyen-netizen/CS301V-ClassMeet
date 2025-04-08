from fastapi import Depends, HTTPException
from pydantic import BaseModel
from app.utils.auth import verify_password, create_jwt_token, verify_jwt_token  # Thêm import verify_jwt_token
from app.dao.user_dao import UserDAO


class LoginRequest(BaseModel):
    email: str
    password: str


async def login(login_data: LoginRequest):
    dao = UserDAO()
    user = dao.find_by_email(login_data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    jwt_token = create_jwt_token({"sub": user["user_id"], "email": user["email"]})
    return {"token": jwt_token, "expiresIn": 3600}


async def logout(token: str = Depends(verify_jwt_token)):
    return {"message": "Logout successful"}