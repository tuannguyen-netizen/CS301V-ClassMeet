import logging
from bson import ObjectId
from datetime import datetime
from dao.db_config import Database
from management.models import Meeting, MeetingParticipant

logger = logging.getLogger(__name__)

class MeetingDAO:
    """Data Access Object for Meeting-related operations"""

    def __init__(self):
        db = Database.get_instance().db
        self.meeting_collection = db.meetings
        self.participant_collection = db.meeting_participants
        logger.info("MeetingDAO initialized")

    async def create_meeting(self, meeting):
        """Create a new meeting in the database"""
        meeting_dict = meeting.to_dict()
        result = await self.meeting_collection.insert_one(meeting_dict)
        return str(result.inserted_id)

    async def find_by_id(self, meeting_id):
        """Find a meeting by its ID"""
        meeting_data = await self.meeting_collection.find_one({"_id": ObjectId(meeting_id)})
        if meeting_data:
            meeting_data["meeting_id"] = str(meeting_data.pop("_id"))
            return Meeting.from_dict(meeting_data)
        return None

    async def end_meeting(self, meeting_id):
        """End a meeting and update the end time"""
        result = await self.meeting_collection.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": {"end_time": datetime.utcnow(), "status": "ended"}}
        )
        return result.modified_count > 0

    async def add_participant(self, participant):
        """Add a participant to a meeting (prevent duplicates)"""
        participant_dict = participant.to_dict()
        existing = await self.participant_collection.find_one({
            "meeting_id": participant.meeting_id,
            "user_id": participant.user_id
        })
        if existing:
            logger.info("User has already joined this meeting.")
            return str(existing["_id"])

        result = await self.participant_collection.insert_one(participant_dict)
        return str(result.inserted_id)

    async def record_participant_left(self, meeting_id, user_id):
        """Record when a participant leaves a meeting"""
        result = await self.participant_collection.update_one(
            {
                "meeting_id": meeting_id,
                "user_id": user_id,
                "status": "joined"
            },
            {
                "$set": {
                    "left_at": datetime.utcnow(),
                    "status": "left"
                }
            }
        )
        return result.modified_count > 0

    async def get_meeting_participants(self, meeting_id, active_only=False):
        """Get all participants of a meeting"""
        query = {"meeting_id": meeting_id}
        if active_only:
            query["status"] = "joined"

        cursor = self.participant_collection.find(query)
        participants = []

        async for participant_data in cursor:
            participant_data["participant_id"] = str(participant_data.pop("_id"))
            participants.append(MeetingParticipant.from_dict(participant_data))

        return participants
