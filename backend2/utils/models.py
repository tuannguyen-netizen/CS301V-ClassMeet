# utils/models.py
from datetime import datetime
from bson import ObjectId
import random
import string
import bcrypt


class User:
    """User model representing a user in the system"""

    def __init__(self, username, email, password=None, user_id=None, created_at=None, updated_at=None):
        self.user_id = user_id if user_id else str(ObjectId())
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def _hash_password(self, password):
        """Hash a password for secure storage"""
        if not password:
            return None
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password):
        """Verify a password against the stored hash"""
        if not password or not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)

    def to_dict(self):
        """Convert user object to dictionary (public data)"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_db_dict(self):
        """Convert user object to dictionary for database storage"""
        user_dict = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        # Convert user_id to _id for MongoDB
        if hasattr(self, 'user_id') and self.user_id:
            user_dict["_id"] = ObjectId(self.user_id)

        return user_dict

    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary"""
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
    """Class model representing a class or course in the system"""

    def __init__(self, class_name, created_by, description=None, class_id=None,
                 class_code=None, created_at=None, updated_at=None):
        self.class_id = class_id if class_id else str(ObjectId())
        self.class_name = class_name
        self.description = description
        self.created_by = created_by  # User ID of the creator
        self.class_code = class_code if class_code else self._generate_class_code()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def _generate_class_code(self):
        """Generate a unique 6-character class code"""
        # Combination of letters and numbers
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(6))

    def to_dict(self):
        """Convert class object to dictionary"""
        class_dict = {
            "class_name": self.class_name,
            "description": self.description,
            "created_by": self.created_by,
            "class_code": self.class_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        if hasattr(self, 'class_id') and self.class_id:
            if not self.class_id.startswith('ObjectId'):
                class_dict["_id"] = ObjectId(self.class_id)

        return class_dict

    @classmethod
    def from_dict(cls, data):
        """Create class object from dictionary"""
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
    """Model representing the relationship between a user and a class"""

    # Role constants
    ROLE_CREATOR = "creator"
    ROLE_MEMBER = "member"

    # Status constants
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"

    def __init__(self, class_id, user_id, role, status=None,
                 membership_id=None, joined_at=None, updated_at=None):
        self.membership_id = membership_id if membership_id else str(ObjectId())
        self.class_id = class_id
        self.user_id = user_id
        self.role = role  # 'creator' or 'member'
        self.status = status if status else self.STATUS_APPROVED  # Default to approved
        self.joined_at = joined_at if joined_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        """Convert membership object to dictionary"""
        membership_dict = {
            "class_id": self.class_id,
            "user_id": self.user_id,
            "role": self.role,
            "status": self.status,
            "joined_at": self.joined_at,
            "updated_at": self.updated_at
        }

        if hasattr(self, 'membership_id') and self.membership_id:
            if not self.membership_id.startswith('ObjectId'):
                membership_dict["_id"] = ObjectId(self.membership_id)

        return membership_dict

    @classmethod
    def from_dict(cls, data):
        """Create membership object from dictionary"""
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
    """Meeting model representing an online meeting in a class"""

    def __init__(self, class_id, created_by, title=None, description=None,
                 meeting_id=None, start_time=None, end_time=None,
                 created_at=None, updated_at=None, status="scheduled"):
        self.meeting_id = meeting_id if meeting_id else str(ObjectId())
        self.class_id = class_id
        self.created_by = created_by  # User ID of the meeting creator
        self.title = title
        self.description = description
        self.start_time = start_time if start_time else datetime.utcnow()
        self.end_time = end_time
        self.status = status  # 'scheduled', 'ongoing', 'ended'
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        """Convert meeting object to dictionary"""
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

        if hasattr(self, 'meeting_id') and self.meeting_id:
            if not self.meeting_id.startswith('ObjectId'):
                meeting_dict["_id"] = ObjectId(self.meeting_id)

        return meeting_dict

    @classmethod
    def from_dict(cls, data):
        """Create meeting object from dictionary"""
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
    """Model representing a participant in a meeting"""

    def __init__(self, meeting_id, user_id, participant_id=None,
                 joined_at=None, left_at=None, status="joined"):
        self.participant_id = participant_id if participant_id else str(ObjectId())
        self.meeting_id = meeting_id
        self.user_id = user_id
        self.joined_at = joined_at if joined_at else datetime.utcnow()
        self.left_at = left_at  # Will be None until the user leaves
        self.status = status  # 'joined', 'left'

    def to_dict(self):
        """Convert participant object to dictionary"""
        participant_dict = {
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "joined_at": self.joined_at,
            "left_at": self.left_at,
            "status": self.status
        }

        if hasattr(self, 'participant_id') and self.participant_id:
            if not self.participant_id.startswith('ObjectId'):
                participant_dict["_id"] = ObjectId(self.participant_id)

        return participant_dict

    @classmethod
    def from_dict(cls, data):
        """Create participant object from dictionary"""
        return cls(
            meeting_id=data.get("meeting_id"),
            user_id=data.get("user_id"),
            participant_id=data.get("participant_id") or str(data.get("_id", "")),
            joined_at=data.get("joined_at"),
            left_at=data.get("left_at"),
            status=data.get("status", "joined")
        )


class ChatMessage:
    """Model representing a chat message in a meeting"""

    def __init__(self, meeting_id, user_id, content, message_id=None, sent_at=None):
        self.message_id = message_id if message_id else str(ObjectId())
        self.meeting_id = meeting_id
        self.user_id = user_id
        self.content = content
        self.sent_at = sent_at if sent_at else datetime.utcnow()

    def to_dict(self):
        """Convert message object to dictionary"""
        message_dict = {
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "content": self.content,
            "sent_at": self.sent_at
        }

        if hasattr(self, 'message_id') and self.message_id:
            if not self.message_id.startswith('ObjectId'):
                message_dict["_id"] = ObjectId(self.message_id)

        return message_dict

    @classmethod
    def from_dict(cls, data):
        """Create message object from dictionary"""
        return cls(
            meeting_id=data.get("meeting_id"),
            user_id=data.get("user_id"),
            content=data.get("content"),
            message_id=data.get("message_id") or str(data.get("_id", "")),
            sent_at=data.get("sent_at")
        )