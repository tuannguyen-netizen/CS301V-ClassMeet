from datetime import datetime
from bson import ObjectId
import bcrypt

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
        return bcrypt.hashpw(password.encode("utf-8"), salt)

    def verify_password(self, password):
        if not password or not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)

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