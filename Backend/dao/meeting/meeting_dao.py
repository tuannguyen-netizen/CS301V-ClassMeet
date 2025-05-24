import logging
from bson import ObjectId
from fastapi import HTTPException
from dao.db_config import Database
from dao.meeting.object import Meeting
from dao.meeting.meeting_interface import MeetingDAOInterface

logger = logging.getLogger(__name__)

class MeetingDAO(MeetingDAOInterface):
    def __init__(self):
        self.db = Database.get_instance().db
        self.collection = self.db.meetings
        logger.info("MeetingDAO initialized")

    async def create_meeting(self, meeting):
        meeting_dict = meeting.to_dict()
        result = await self.collection.insert_one(meeting_dict)
        return str(result.inserted_id)

    async def find_by_id(self, meeting_id):
        meeting_data = await self.collection.find_one({"_id": ObjectId(meeting_id)})
        if meeting_data:
            return Meeting.from_dict(meeting_data)
        return None

    async def add_user_to_meeting(self, meeting_id: str, user_id: str):
        participant = {
            "meeting_id": meeting_id,
            "user_id": user_id,
            "joined_at": datetime.utcnow()
        }
        try:
            await self.db.meeting_participants.insert_one(participant)
        except Exception as e:
            if "duplicate key error" in str(e):
                raise HTTPException(status_code=400, detail="User already in meeting")
            raise e

    async def remove_user_from_meeting(self, meeting_id: str, user_id: str):
        result = await self.db.meeting_participants.delete_one({"meeting_id": meeting_id, "user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not in meeting")

    async def get_meeting_participants(self, meeting_id: str):
        participants = await self.db.meeting_participants.find({"meeting_id": meeting_id}).to_list(None)
        return [{"user_id": p["user_id"]} for p in participants]