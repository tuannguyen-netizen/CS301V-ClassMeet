# management/auth_manager.py
import logging
from fastapi import HTTPException
from dao.user_dao import UserDAO
from management.models import UserRegistrationRequest, UserLoginRequest, TokenResponse
from management.auth import create_access_token
from management.helpers import validate_email, validate_password, validate_username
from management.models import User

logger = logging.getLogger(__name__)
user_dao = UserDAO()

async def register_user(user_data: UserRegistrationRequest) -> TokenResponse:
    logger.info(f"Registration request received for email: {user_data.email}")

    validate_email(user_data.email)
    validate_password(user_data.password)
    validate_username(user_data.username)

    if await user_dao.find_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already in use")

    if await user_dao.find_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already in use")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    user_id = await user_dao.create_user(new_user)
    logger.info(f"New user created with ID: {user_id}")

    token = create_access_token(user_id)
    return TokenResponse(token=token, expires_in=3600)

async def login_user(login_data: UserLoginRequest) -> TokenResponse:
    logger.info(f"Login request received for email: {login_data.email}")

    user = await user_dao.find_by_email(login_data.email)
    if not user or not user.verify_password(login_data.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.user_id)
    return TokenResponse(token=token, expires_in=3600)
