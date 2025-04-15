import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.dao.user_dao import UserDAO
from app.models.user import User
from app.utils.auth import create_access_token, get_current_user
from app.utils.helpers import validate_email, validate_password, validate_username, format_success_response

logger = logging.getLogger(__name__)

router = APIRouter()
user_dao = UserDAO()


class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    token: str
    expires_in: int


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegistrationRequest):
    """Register a new user"""
    logger.info(f"Registration request received for email: {user_data.email}")
    try:
        # Validate input data
        validate_email(user_data.email)
        validate_password(user_data.password)
        validate_username(user_data.username)

        # Check if email exists
        existing_user = await user_dao.find_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Email already in use: {user_data.email}")
            raise HTTPException(status_code=400, detail="Email already in use")

        # Check if username exists
        existing_username = await user_dao.find_by_username(user_data.username)
        if existing_username:
            logger.warning(f"Username already in use: {user_data.username}")
            raise HTTPException(status_code=400, detail="Username already in use")

        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )

        # Save to database
        user_id = await user_dao.create_user(new_user)
        logger.info(f"New user created with ID: {user_id}")

        # Create authentication token
        token = create_access_token(user_id)

        return {"token": token, "expires_in": 3600}

    except ValueError as e:
        logger.error(f"Validation error during registration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLoginRequest):
    """Log in a user"""
    logger.info(f"Login request received for email: {login_data.email}")
    try:
        # Find user by email
        user = await user_dao.find_by_email(login_data.email)

        if not user:
            logger.warning(f"Invalid login attempt: user not found for email {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not user.verify_password(login_data.password):
            logger.warning(f"Invalid login attempt: incorrect password for email {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create authentication token
        token = create_access_token(user.user_id)
        logger.info(f"User logged in successfully: {user.user_id}")

        return {"token": token, "expires_in": 3600}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(user_id: str = Depends(get_current_user)):
    """Log out a user"""
    # Note: With JWT, logout actually happens client-side
    # The server doesn't need to do anything special
    logger.info(f"User logged out: {user_id}")
    return format_success_response(message="Successfully logged out")