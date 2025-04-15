from app.config.database import Database
from app.models.meeting import Meeting, MeetingParticipant, ChatMessage
from datetime import datetime
from bson import ObjectId
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)


class MeetingDAO:
    """Data Access Object for Meeting-related operations"""

    def __init__(self):
        db = Database.get_instance().db
        if db is None:
            logger.error("Database connection is None")
            raise ValueError("Database connection failed")
        self.meeting_collection = db.meetings
        self.participant_collection = db.meeting_participants
        self.chat_collection = db.chat_messages
        if self.meeting_collection is None or self.participant_collection is None or self.chat_collection is None:
            logger.error("One or more collections are None")
            raise ValueError("Collections not found")
        logger.info("MeetingDAO initialized with collections")

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

    async def update_meeting(self, meeting):
        """Update a meeting's information"""
        meeting_dict = meeting.to_dict()
        meeting_id = ObjectId(meeting.meeting_id)

        # Remove meeting_id from the dictionary since we're using _id in MongoDB
        meeting_dict.pop("meeting_id", None)

        result = await self.meeting_collection.update_one(
            {"_id": meeting_id},
            {"$set": meeting_dict}
        )
        return result.modified_count > 0

    async def delete_meeting(self, meeting_id):
        """Delete a meeting and all related data"""
        # Delete the meeting
        result = await self.meeting_collection.delete_one({"_id": ObjectId(meeting_id)})

        # Delete all participants info
        await self.participant_collection.delete_many({"meeting_id": meeting_id})

        # Delete all chat messages
        await self.chat_collection.delete_many({"meeting_id": meeting_id})

        return result.deleted_count > 0

    async def end_meeting(self, meeting_id):
        """End a meeting and update the end time"""
        result = await self.meeting_collection.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": {"end_time": datetime.utcnow(), "status": "ended"}}
        )
        return result.modified_count > 0

    async def list_class_meetings(self, class_id):
        """List all meetings for a class"""
        cursor = self.meeting_collection.find({"class_id": class_id}).sort("created_at", -1)
        meetings = []

        async for meeting_data in cursor:
            meeting_data["meeting_id"] = str(meeting_data.pop("_id"))
            meetings.append(Meeting.from_dict(meeting_data))

        return meetings

    # Participant management

    async def add_participant(self, participant):
        """Add a participant to a meeting"""
        # Check if the participant is already in the meeting
        existing = await self.participant_collection.find_one({
            "meeting_id": participant.meeting_id,
            "user_id": participant.user_id,
            "status": "joined"  # Only check for active participants
        })

        if existing:
            return str(existing["_id"])

        # Add new participant
        result = await self.participant_collection.insert_one(participant.to_dict())
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

    async def export_attendance(self, meeting_id, export_format="csv"):
        """Export attendance data for a meeting"""
        # Get meeting information
        meeting = await self.find_by_id(meeting_id)
        if not meeting:
            raise ValueError("Meeting does not exist")

        # Get all participants
        cursor = self.participant_collection.find({"meeting_id": meeting_id})
        attendance_data = []

        async for participant in cursor:
            # Note: We would need to combine with user info from the users table
            attendance_data.append({
                "User ID": participant["user_id"],
                "Joined At": participant["joined_at"],
                "Left At": participant.get("left_at", "Still in meeting"),
                "Duration (minutes)": self._calculate_duration(participant)
            })

        if not attendance_data:
            raise ValueError("No attendance data")

        # Convert to DataFrame
        df = pd.DataFrame(attendance_data)

        # Export in the specified format
        if export_format.lower() == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue()
        elif export_format.lower() == "excel":
            output = io.BytesIO()
            df.to_excel(output, index=False)
            return output.getvalue()
        else:
            raise ValueError("Unsupported format")

    def _calculate_duration(self, participant):
        """Calculate participation duration (minutes)"""
        joined_at = participant["joined_at"]

        if "left_at" in participant and participant["left_at"]:
            left_at = participant["left_at"]
        else:
            left_at = datetime.utcnow()

        duration = (left_at - joined_at).total_seconds() / 60
        return round(duration, 2)

    # Chat message management

    async def add_chat_message(self, message):
        """Add a chat message to a meeting"""
        result = await self.chat_collection.insert_one(message.to_dict())
        return str(result.inserted_id)

    async def get_chat_messages(self, meeting_id, limit=100):
        """Get chat messages for a meeting"""
        cursor = self.chat_collection.find({"meeting_id": meeting_id}).sort("sent_at", 1).limit(limit)
        messages = []

        async for message_data in cursor:
            message_data["message_id"] = str(message_data.pop("_id"))
            messages.append(ChatMessage.from_dict(message_data))

        return messages