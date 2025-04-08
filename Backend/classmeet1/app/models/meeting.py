from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatMessage(BaseModel):
    message_id: int
    user_id: int
    content: str
    sent_at: datetime = datetime.utcnow()

class MeetingParticipant(BaseModel):
    user_id: int
    joined_at: datetime = datetime.utcnow()

class Meeting(BaseModel):
    meeting_id: int
    class_id: int
    user_id: int  # Người tạo cuộc họp
    start_time: datetime
    end_time: datetime
    created_at: datetime = datetime.utcnow()
    participants: List[MeetingParticipant] = []
    chat_messages: List[ChatMessage] = []