from datetime import datetime
from bson import ObjectId


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
        return {
            "meeting_id": self.meeting_id,
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

    @classmethod
    def from_dict(cls, data):
        """Create meeting object from dictionary"""
        return cls(
            class_id=data.get("class_id"),
            created_by=data.get("created_by"),
            title=data.get("title"),
            description=data.get("description"),
            meeting_id=data.get("meeting_id") or data.get("_id"),
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

    def leave_meeting(self):
        """Record when a participant leaves the meeting"""
        self.left_at = datetime.utcnow()
        self.status = "left"

    def to_dict(self):
        """Convert participant object to dictionary"""
        return {
            "participant_id": self.participant_id,
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "joined_at": self.joined_at,
            "left_at": self.left_at,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        """Create participant object from dictionary"""
        return cls(
            meeting_id=data.get("meeting_id"),
            user_id=data.get("user_id"),
            participant_id=data.get("participant_id") or data.get("_id"),
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
        return {
            "message_id": self.message_id,
            "meeting_id": self.meeting_id,
            "user_id": self.user_id,
            "content": self.content,
            "sent_at": self.sent_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create message object from dictionary"""
        return cls(
            meeting_id=data.get("meeting_id"),
            user_id=data.get("user_id"),
            content=data.get("content"),
            message_id=data.get("message_id") or data.get("_id"),
            sent_at=data.get("sent_at")
        )