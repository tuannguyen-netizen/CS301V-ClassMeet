# api/meeting_api.py
from fastapi import APIRouter, HTTPException, Depends, Path, Body, Response
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from dao.class_dao import ClassDAO
from dao.meeting_dao import MeetingDAO
from dao.user_dao import UserDAO
from utils.models import Meeting, MeetingParticipant, ChatMessage
from utils.auth import get_current_user
from utils.helpers import format_success_response

import logging

logger = logging.getLogger(__name__)
router = APIRouter()
class_dao = ClassDAO()
meeting_dao = MeetingDAO()
user_dao = UserDAO()


# Request/Response models
class MeetingCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class MeetingResponse(BaseModel):
    meeting_id: str
    class_id: str
    title: str
    description: Optional[str]
    created_by: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class ChatMessageResponse(BaseModel):
    message_id: str
    user_id: str
    username: str
    content: str
    sent_at: datetime


@router.post("/class/{class_id}/create", response_model=MeetingResponse)
async def create_meeting(
        class_id: str,
        meeting_data: MeetingCreateRequest,
        user_id: str = Depends(get_current_user)
):
    """Create a new meeting in a class"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user is class creator (only creator can create meetings)
    is_creator = await class_dao.is_class_creator(class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can create meetings")

    # Create new meeting
    new_meeting = Meeting(
        class_id=class_id,
        created_by=user_id,
        title=meeting_data.title,
        description=meeting_data.description
    )

    # Save to database
    meeting_id = await meeting_dao.create_meeting(new_meeting)

    # Get created meeting
    created_meeting = await meeting_dao.find_by_id(meeting_id)

    return {
        "meeting_id": created_meeting.meeting_id,
        "class_id": created_meeting.class_id,
        "title": created_meeting.title,
        "description": created_meeting.description,
        "created_by": created_meeting.created_by,
        "start_time": created_meeting.start_time,
        "end_time": created_meeting.end_time,
        "status": created_meeting.status
    }


@router.post("/{meeting_id}/join")
async def join_meeting(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Join a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to join this meeting")

    # Create participation record
    participant = MeetingParticipant(
        meeting_id=meeting_id,
        user_id=user_id
    )

    # Save to database
    await meeting_dao.add_participant(participant)

    return format_success_response(message="Successfully joined the meeting")


@router.post("/{meeting_id}/leave")
async def leave_meeting(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Leave a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Record leave time
    await meeting_dao.record_participant_left(meeting_id, user_id)

    return format_success_response(message="Successfully left the meeting")


@router.post("/{meeting_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
        meeting_id: str,
        message_data: ChatMessageRequest,
        user_id: str = Depends(get_current_user)
):
    """Send a chat message in a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to participate in this meeting")

    # Create new message
    message = ChatMessage(
        meeting_id=meeting_id,
        user_id=user_id,
        content=message_data.content
    )

    # Save to database
    message_id = await meeting_dao.add_chat_message(message)

    # Get user info
    user = await user_dao.find_by_id(user_id)

    return {
        "message_id": message_id,
        "user_id": user_id,
        "username": user.username,
        "content": message.content,
        "sent_at": message.sent_at
    }


@router.get("/{meeting_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat_messages(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Get chat messages for a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to view this meeting's chat")

    # Get chat messages
    messages = await meeting_dao.get_chat_messages(meeting_id)

    result = []
    for message in messages:
        # Get user details
        user = await user_dao.find_by_id(message.user_id)
        if user:
            result.append({
                "message_id": message.message_id,
                "user_id": message.user_id,
                "username": user.username,
                "content": message.content,
                "sent_at": message.sent_at
            })

    return result


@router.get("/{meeting_id}/interface", response_class=HTMLResponse)
async def get_meeting_interface(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Get HTML interface for the meeting"""
    # This would normally be handled by a frontend framework like React
    # For simplicity, we're returning an HTML template from the backend

    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to join this meeting")

    # Return the meeting interface HTML (simplified for this example)
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClassMeet Video Meeting</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
            .container { display: flex; height: 100vh; }
            .video-container { flex: 1; display: flex; flex-wrap: wrap; background: #f0f0f0; }
            .video-item { width: 320px; height: 240px; margin: 10px; background: #000; }
            .chat-container { width: 300px; border-left: 1px solid #ccc; display: flex; flex-direction: column; }
            .chat-messages { flex: 1; overflow-y: auto; padding: 10px; }
            .chat-input { padding: 10px; border-top: 1px solid #ccc; }
            .controls { position: fixed; bottom: 20px; left: 0; right: 0; text-align: center; }
            .controls button { margin: 0 5px; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="video-container" id="videoContainer">
                <!-- Videos will be added here dynamically -->
            </div>
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <!-- Chat messages will be added here dynamically -->
                </div>
                <div class="chat-input">
                    <input type="text" id="messageInput" placeholder="Type a message...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        <div class="controls">
            <button id="cameraBtn" onclick="toggleCamera()">Turn on camera</button>
            <button id="micBtn" onclick="toggleMicrophone()">Turn on microphone</button>
            <button id="leaveBtn" onclick="leaveMeeting()">Leave Meeting</button>
        </div>

        <script>
            // JavaScript for controlling the meeting interface would go here
            // This includes WebSocket connection, video/audio controls, etc.
        </script>
    </body>
    </html>
    """