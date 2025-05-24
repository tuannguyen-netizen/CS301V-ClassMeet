from fastapi import APIRouter, HTTPException
from dao.user.interface import UserRegistrationRequest, UserLoginRequest, TokenResponse
from management.management import register_user, login_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegistrationRequest):
    try:
        return await register_user(user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest):
    try:
        return await login_user(login_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))