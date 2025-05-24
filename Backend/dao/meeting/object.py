from datetime import datetime
from bson import ObjectId

class Meeting:
    def __init__(self, title, class_id, created_by, start_time=None, end_time=None, meeting_id=None):
        self.meeting_id = meeting_id if meeting_id else str(ObjectId())
        self.title = title
        self.class_id = class_id
        self.created_by = created_by
        self.start_time = start_time if start_time else datetime.utcnow()
        self.end_time = end_time
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": ObjectId(self.meeting_id),
            "title": self.title,
            "class_id": self.class_id,
            "created_by": self.created_by,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title"),
            class_id=data.get("class_id"),
            created_by=data.get("created_by"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            meeting_id=str(data.get("_id"))
        )