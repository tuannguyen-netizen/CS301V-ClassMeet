from fastapi import APIRouter, Depends, HTTPException
from management.auth import get_current_user
from dao.meeting.interface import MeetingCreateRequest, MeetingResponse
from management.management import create_meeting, join_meeting, leave_meeting

router = APIRouter()

@router.post("/create", response_model=MeetingResponse)
async def create(data: MeetingCreateRequest, user_id: str = Depends(get_current_user)):
    return await create_meeting(data, user_id)

@router.post("/{meeting_id}/join")
async def join(meeting_id: str, user_id: str = Depends(get_current_user)):
    return await join_meeting(meeting_id, user_id)

@router.post("/{meeting_id}/leave")
async def leave(meeting_id: str, user_id: str = Depends(get_current_user)):
    return await leave_meeting(meeting_id, user_id)