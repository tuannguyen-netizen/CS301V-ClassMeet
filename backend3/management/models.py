# management/models.py
from datetime import datetime
from bson import ObjectId
import bcrypt
import random
import string

from pydantic import BaseModel, Field
from typing import Optional, List


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

# Pydantic models for Class API
class ClassCreateRequest(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ClassJoinRequest(BaseModel):
    class_code: str = Field(..., min_length=6, max_length=6)

class ClassResponse(BaseModel):
    class_id: str
    class_name: str
    description: Optional[str]
    class_code: str
    created_by: str
    is_creator: bool

class ClassMemberResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str

class MeetingCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class MeetingResponse(BaseModel):
    meeting_id: str
    class_id: str
    title: str
    description: Optional[str]
    created_by: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str

class User:
    def __init__(self, username, email, password=None, user_id=None, created_at=None, updated_at=None):
        self.user_id = user_id if user_id else str(ObjectId())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def _hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password):
        if not password or not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_db_dict(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.user_id:
            user_dict["_id"] = ObjectId(self.user_id)
        return user_dict

    @classmethod
    def from_dict(cls, data):
        user = cls(
            username=data.get("username"),
            email=data.get("email"),
            user_id=data.get("user_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        user.password_hash = data.get("password_hash")
        return user


class Class:
    def __init__(self, class_name, created_by, description=None, class_id=None,
                 class_code=None, created_at=None, updated_at=None):
        self.class_id = class_id if class_id else str(ObjectId())
        self.class_name = class_name
        self.description = description
        self.created_by = created_by
        self.class_code = class_code if class_code else self._generate_class_code()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def _generate_class_code(self):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def to_dict(self):
        class_dict = {
            "class_name": self.class_name,
            "description": self.description,
            "created_by": self.created_by,
            "class_code": self.class_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.class_id:
            class_dict["_id"] = ObjectId(self.class_id)
        return class_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            class_name=data.get("class_name"),
            created_by=data.get("created_by"),
            description=data.get("description"),
            class_id=data.get("class_id"),
            class_code=data.get("class_code"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class ClassMembership:
    ROLE_CREATOR = "creator"
    ROLE_MEMBER = "member"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"

    def __init__(self, class_id, user_id, role, status=None,
                 membership_id=None, joined_at=None, updated_at=None):
        self.membership_id = membership_id if membership_id else str(ObjectId())
        self.class_id = class_id
        self.user_id = user_id
        self.role = role
        self.status = status if status else self.STATUS_APPROVED
        self.joined_at = joined_at if joined_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        membership_dict = {
            "class_id": self.class_id,
            "user_id": self.user_id,
            "role": self.role,
            "status": self.status,
            "joined_at": self.joined_at,
            "updated_at": self.updated_at
        }
        if self.membership_id:
            membership_dict["_id"] = ObjectId(self.membership_id)
        return membership_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            class_id=data.get("class_id"),
            user_id=data.get("user_id"),
            role=data.get("role"),
            status=data.get("status"),
            membership_id=data.get("membership_id") or str(data.get("_id", "")),
            joined_at=data.get("joined_at"),
            updated_at=data.get("updated_at")
        )


class Meeting:
    def __init__(self, class_id, created_by, title=None, description=None,
                 meeting_id=None, start_time=None, end_time=None,
                 created_at=None, updated_at=None, status="scheduled"):
        self.meeting_id = meeting_id if meeting_id else str(ObjectId())
        self.class_id = class_id
        self.created_by = created_by
        self.title = title
        self.description = description
        self.start_time = start_time if start_time else datetime.utcnow()
        self.end_time = end_time
        self.status = status
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        meeting_dict = {
            "class_id": self.class_id,
            "created_by": self.created_by,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.meeting_id:
            meeting_dict["_id"] = ObjectId(self.meeting_id)
        return meeting_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            class_id=data.get("class_id"),
            created_by=data.get("created_by"),
            title=data.get("title"),
            description=data.get("description"),
            meeting_id=data.get("meeting_id"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            status=data.get("status", "scheduled"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


class MeetingParticipant:
    def __init__(self, meeting_id, user_id, participant_id=None,
                 joined_at=None, left_at=None, status="joined"):
        self.participant_id = participant_id if participant_id else str(ObjectId())
        self.meeting_id = meeting_id
        self.user_id = user_id
        self.joined_at = joined_at if joined_at else datetime.utcnow()
        self.left_at = left_at
        self.status = status

    def to_dict(self):
        participant_dict = {
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "joined_at": self.joined_at,
            "left_at": self.left_at,
            "status": self.status
        }
        if self.participant_id:
            participant_dict["_id"] = ObjectId(self.participant_id)
        return participant_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            meeting_id=data.get("meeting_id"),
            user_id=data.get("user_id"),
            participant_id=data.get("participant_id") or str(data.get("_id", "")),
            joined_at=data.get("joined_at"),
            left_at=data.get("left_at"),
            status=data.get("status", "joined")
        )
