from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.dao.user_dao import UserDAO
from app.utils.auth import get_current_user
from app.utils.helpers import validate_email, format_success_response

router = APIRouter()
user_dao = UserDAO()


class UserUpdateRequest(BaseModel):
    username: str = Field(None, min_length=3, max_length=50)
    email: str = Field(None, max_length=100)


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    """Get current user's information"""
    user = await user_dao.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email
    }


@router.put("/me", response_model=UserResponse)
async def update_user_info(
        user_data: UserUpdateRequest,
        user_id: str = Depends(get_current_user)
):
    """Update current user's information"""
    # Get current user information
    user = await user_dao.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update information if provided
    if user_data.username:
        # Check if username already exists
        existing_user = await user_dao.find_by_username(user_data.username)
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(status_code=400, detail="Username already in use")
        user.username = user_data.username

    if user_data.email:
        # Validate email
        validate_email(user_data.email)

        # Check if email already exists
        existing_user = await user_dao.find_by_email(user_data.email)
        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_data.email

    # Save changes to database
    await user_dao.update_user(user)

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email
    }