from fastapi import HTTPException
from dao.user.user_dao import UserDAO
from dao.classes.class_dao import ClassDAO
from dao.meeting.meeting_dao import MeetingDAO
from dao.user.object import User
from dao.classes.object import Class
from dao.meeting.object import Meeting
from dao.user.interface import UserRegistrationRequest, UserLoginRequest
from dao.classes.interface import ClassCreateRequest, ClassJoinRequest, ClassResponse
from dao.meeting.interface import MeetingCreateRequest, MeetingResponse
from datetime import datetime, timedelta
import jwt
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION"))
ALGORITHM = "HS256"

# Initialize DAOs
user_dao = UserDAO()
class_dao = ClassDAO()
meeting_dao = MeetingDAO()

# User Management
async def register_user(request: UserRegistrationRequest):
    logger.info(f"Registration request for email: {request.email}")
    if await user_dao.find_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await user_dao.find_by_username(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(username=request.username, email=request.email, password=request.password)
    user_id = await user_dao.create_user(new_user)
    logger.info(f"User created with ID: {user_id}")

    token = create_access_token(user_id)
    return {"token": token, "expires_in": JWT_EXPIRATION * 60}

async def login_user(request: UserLoginRequest):
    logger.info(f"Login request for email: {request.email}")
    user = await user_dao.find_by_email(request.email)
    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.user_id)
    return {"token": token, "expires_in": JWT_EXPIRATION * 60}

# Class Management
async def create_class(data: ClassCreateRequest, user_id: str):
    logger.info(f"Create class request for: {data.class_name}")
    new_class = Class(class_name=data.class_name, created_by=user_id, description=data.description)
    if await class_dao.find_by_class_code(new_class.class_code):
        raise HTTPException(status_code=400, detail="Class code already exists")
    class_id = await class_dao.create_class(new_class)
    created_class = await class_dao.find_by_id(class_id)
    return ClassResponse(
        class_id=created_class.class_id,
        class_name=created_class.class_name,
        description=created_class.description,
        class_code=created_class.class_code,
        created_by=created_class.created_by
    )

async def join_class(data: ClassJoinRequest, user_id: str):
    logger.info(f"User {user_id} joining class with code: {data.class_code}")
    class_obj = await class_dao.find_by_class_code(data.class_code)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    await class_dao.add_user_to_class(class_obj.class_id, user_id)
    return ClassResponse(
        class_id=class_obj.class_id,
        class_name=class_obj.class_name,
        description=class_obj.description,
        class_code=class_obj.class_code,
        created_by=class_obj.created_by
    )

async def get_user_classes(user_id: str):
    logger.info(f"Fetching classes for user: {user_id}")
    memberships = await class_dao.get_user_memberships(user_id)
    classes = []
    for membership in memberships:
        class_obj = await class_dao.find_by_id(membership["class_id"])
        if class_obj:
            classes.append(ClassResponse(
                class_id=class_obj.class_id,
                class_name=class_obj.class_name,
                description=class_obj.description,
                class_code=class_obj.class_code,
                created_by=class_obj.created_by
            ))
    return classes

# Meeting Management
async def create_meeting(data: MeetingCreateRequest, user_id: str):
    logger.info(f"Create meeting request for: {data.title}")
    new_meeting = Meeting(
        title=data.title,
        class_id=data.class_id,
        created_by=user_id,
        start_time=datetime.fromisoformat(data.start_time),
        end_time=datetime.fromisoformat(data.end_time)
    )
    class_obj = await class_dao.find_by_id(data.class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    meeting_id = await meeting_dao.create_meeting(new_meeting)
    created_meeting = await meeting_dao.find_by_id(meeting_id)
    return MeetingResponse(
        meeting_id=created_meeting.meeting_id,
        title=created_meeting.title,
        class_id=created_meeting.class_id,
        created_by=created_meeting.created_by,
        start_time=created_meeting.start_time.isoformat(),
        end_time=created_meeting.end_time.isoformat() if created_meeting.end_time else None
    )

async def join_meeting(meeting_id: str, user_id: str):
    logger.info(f"User {user_id} joining meeting: {meeting_id}")
    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await meeting_dao.add_user_to_meeting(meeting_id, user_id)
    return {"message": "User successfully joined the meeting"}

async def leave_meeting(meeting_id: str, user_id: str):
    logger.info(f"User {user_id} leaving meeting: {meeting_id}")
    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await meeting_dao.remove_user_from_meeting(meeting_id, user_id)
    return {"message": "User successfully left the meeting"}

# Helper Functions
def create_access_token(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)