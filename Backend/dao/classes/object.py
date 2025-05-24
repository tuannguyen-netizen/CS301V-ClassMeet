from datetime import datetime
from bson import ObjectId
import secrets

class Class:
    def __init__(self, class_name, created_by, description=None, class_id=None, class_code=None, created_at=None, updated_at=None):
        self.class_id = class_id if class_id else str(ObjectId())
        self.class_name = class_name
        self.description = description
        self.created_by = created_by
        self.class_code = class_code if class_code else secrets.token_urlsafe(8)
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

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