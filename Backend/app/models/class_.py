from datetime import datetime
from bson import ObjectId
import random
import string


class Class:
    """Class model representing a class or course in the system"""

    def __init__(self, class_name, created_by, description=None, class_id=None,
                 class_code=None, created_at=None, updated_at=None):
        self.class_id = class_id if class_id else str(ObjectId())
        self.class_name = class_name
        self.description = description
        self.created_by = created_by  # User ID of the creator (leader)
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
        return {
            "class_id": self.class_id,
            "class_name": self.class_name,
            "description": self.description,
            "created_by": self.created_by,
            "class_code": self.class_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create class object from dictionary"""
        return cls(
            class_name=data.get("class_name"),
            created_by=data.get("created_by"),
            description=data.get("description"),
            class_id=data.get("class_id") or data.get("_id"),
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
        return {
            "membership_id": self.membership_id,
            "class_id": self.class_id,
            "user_id": self.user_id,
            "role": self.role,
            "status": self.status,
            "joined_at": self.joined_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create membership object from dictionary"""
        return cls(
            class_id=data.get("class_id"),
            user_id=data.get("user_id"),
            role=data.get("role"),
            status=data.get("status"),
            membership_id=data.get("membership_id") or data.get("_id"),
            joined_at=data.get("joined_at"),
            updated_at=data.get("updated_at")
        )