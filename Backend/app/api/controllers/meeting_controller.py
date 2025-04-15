from fastapi import APIRouter, HTTPException, Depends, Path, Body, Response
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.dao.class_dao import ClassDAO
from app.dao.meeting_dao import MeetingDAO
from app.dao.user_dao import UserDAO
from app.models.meeting import Meeting, MeetingParticipant, ChatMessage
from app.utils.auth import get_current_user
from app.utils.helpers import format_success_response

router = APIRouter()
class_dao = ClassDAO()
meeting_dao = MeetingDAO()
user_dao = UserDAO()


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


class MeetingParticipantResponse(BaseModel):
    user_id: str
    username: str
    joined_at: datetime
    left_at: Optional[datetime]
    status: str


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class ChatMessageResponse(BaseModel):
    message_id: str
    user_id: str
    username: str
    content: str
    sent_at: datetime


@router.post("/class/{class_id}/meeting", response_model=MeetingResponse)
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


@router.get("/class/{class_id}/meetings", response_model=List[MeetingResponse])
async def get_class_meetings(
        class_id: str,
        user_id: str = Depends(get_current_user)
):
    """Get a list of meetings for a class"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this class")

    # Get meetings
    meetings = await meeting_dao.list_class_meetings(class_id)

    result = []
    for meeting in meetings:
        result.append({
            "meeting_id": meeting.meeting_id,
            "class_id": meeting.class_id,
            "title": meeting.title,
            "description": meeting.description,
            "created_by": meeting.created_by,
            "start_time": meeting.start_time,
            "end_time": meeting.end_time,
            "status": meeting.status
        })

    return result


@router.get("/meeting/{meeting_id}", response_model=MeetingResponse)
async def get_meeting_details(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Get details of a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to view this meeting")

    return {
        "meeting_id": meeting.meeting_id,
        "class_id": meeting.class_id,
        "title": meeting.title,
        "description": meeting.description,
        "created_by": meeting.created_by,
        "start_time": meeting.start_time,
        "end_time": meeting.end_time,
        "status": meeting.status
    }


@router.post("/meeting/{meeting_id}/join")
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


@router.post("/meeting/{meeting_id}/leave")
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


@router.post("/meeting/{meeting_id}/end")
async def end_meeting(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """End a meeting (only class creator)"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is the class creator
    is_creator = await class_dao.is_class_creator(meeting.class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can end the meeting")

    # End meeting
    await meeting_dao.end_meeting(meeting_id)

    return format_success_response(message="Meeting ended successfully")


@router.get("/meeting/{meeting_id}/participants", response_model=List[MeetingParticipantResponse])
async def get_meeting_participants(
        meeting_id: str,
        user_id: str = Depends(get_current_user)
):
    """Get a list of meeting participants"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is a member of the class
    is_member = await class_dao.is_class_member(meeting.class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You don't have permission to view this meeting")

    # Get participants
    participants = await meeting_dao.get_meeting_participants(meeting_id)

    result = []
    for participant in participants:
        # Get user details
        user = await user_dao.find_by_id(participant.user_id)
        if user:
            result.append({
                "user_id": participant.user_id,
                "username": user.username,
                "joined_at": participant.joined_at,
                "left_at": participant.left_at,
                "status": participant.status
            })

    return result


@router.get("/meeting/{meeting_id}/attendance")
async def export_attendance(
        meeting_id: str,
        format: str = "csv",
        user_id: str = Depends(get_current_user)
):
    """Export attendance data for a meeting"""
    # Check if meeting exists
    meeting = await meeting_dao.find_by_id(meeting_id)

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Check if user is the class creator
    is_creator = await class_dao.is_class_creator(meeting.class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can export attendance data")

    try:
        # Export attendance data
        attendance_data = await meeting_dao.export_attendance(meeting_id, format)

        # Return file
        content_type = "text/csv" if format.lower() == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"attendance_{meeting_id}.{format.lower()}"

        return StreamingResponse(
            iter([attendance_data]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/meeting/{meeting_id}/chat", response_model=ChatMessageResponse)
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


@router.get("/meeting/{meeting_id}/chat", response_model=List[ChatMessageResponse])
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