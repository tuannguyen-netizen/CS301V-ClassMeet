# api/meeting_api.py
from fastapi import APIRouter, Depends
from typing import List
from management.auth import get_current_user
from management.models import (
    MeetingCreateRequest, MeetingResponse,
    ChatMessageRequest, ChatMessageResponse
)
from management.meeting_manager import (
    create_meeting, join_meeting, leave_meeting,
    send_chat_message, get_chat_messages
)

router = APIRouter()

@router.post("/class/{class_id}/create", response_model=MeetingResponse)
async def create(class_id: str, meeting_data: MeetingCreateRequest, user_id: str = Depends(get_current_user)):
    return await create_meeting(class_id, meeting_data, user_id)

@router.post("/{meeting_id}/join")
async def join(meeting_id: str, user_id: str = Depends(get_current_user)):
    return await join_meeting(meeting_id, user_id)

@router.post("/{meeting_id}/leave")
async def leave(meeting_id: str, user_id: str = Depends(get_current_user)):
    return await leave_meeting(meeting_id, user_id)

@router.post("/{meeting_id}/chat", response_model=ChatMessageResponse)
async def chat(meeting_id: str, message_data: ChatMessageRequest, user_id: str = Depends(get_current_user)):
    return await send_chat_message(meeting_id, message_data, user_id)

@router.get("/{meeting_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat(meeting_id: str, user_id: str = Depends(get_current_user)):
    return await get_chat_messages(meeting_id, user_id)
