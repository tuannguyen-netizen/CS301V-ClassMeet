from datetime import datetime
from bson import ObjectId
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

    def update_password(self, new_password):
        """Update user's password"""
        self.password_hash = self._hash_password(new_password)
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def to_db_dict(self):
        """Convert user object to dictionary for database storage"""
        user_dict = self.to_dict()
        user_dict["password_hash"] = self.password_hash
        return user_dict

    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary"""
        user = cls(
            username=data.get("username"),
            email=data.get("email"),
            user_id=data.get("user_id") or data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        user.password_hash = data.get("password_hash")
        return user