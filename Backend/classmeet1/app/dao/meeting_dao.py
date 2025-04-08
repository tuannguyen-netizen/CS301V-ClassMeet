from app.config.database import get_db
from app.models.meeting import Meeting

class MeetingDAO:
    def __init__(self):
        self.collection = get_db()["meetings"]

    def create(self, meeting: Meeting):
        return self.collection.insert_one(meeting.dict())

    def find_by_id(self, meeting_id: int):
        return self.collection.find_one({"meeting_id": meeting_id})

    def add_participant(self, meeting_id: int, participant: dict):
        return self.collection.update_one(
            {"meeting_id": meeting_id},
            {"$push": {"participants": participant}}
        )

    def add_chat_message(self, meeting_id: int, message: dict):
        return self.collection.update_one(
            {"meeting_id": meeting_id},
            {"$push": {"chat_messages": message}}
        )

    def get_participants(self, meeting_id: int):
        meeting = self.find_by_id(meeting_id)
        return meeting.get("participants", [])