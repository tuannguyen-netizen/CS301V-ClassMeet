# management/meeting_manager.py
from fastapi import HTTPException, WebSocket
from dao.class_dao import ClassDAO
from dao.meeting_dao import MeetingDAO
from dao.user_dao import UserDAO
from management.models import (
    MeetingCreateRequest, MeetingResponse,
    Meeting, MeetingParticipant
)
from management.video_server import ConnectionManager
import json

class_dao = ClassDAO()
meeting_dao = MeetingDAO()
user_dao = UserDAO()

async def create_meeting(class_id: str, data: MeetingCreateRequest, user_id: str) -> MeetingResponse:
    class_obj = await class_dao.find_by_id(class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not await class_dao.is_class_creator(class_id, user_id):
        raise HTTPException(status_code=403, detail="Only the class creator can create meetings")

    meeting = Meeting(class_id=class_id, created_by=user_id, title=data.title, description=data.description)
    meeting_id = await meeting_dao.create_meeting(meeting)
    created = await meeting_dao.find_by_id(meeting_id)

    return MeetingResponse(
        meeting_id=created.meeting_id,
        class_id=created.class_id,
        title=created.title,
        description=created.description,
        created_by=created.created_by,
        start_time=created.start_time,
        end_time=created.end_time,
        status=created.status
    )

async def join_meeting(meeting_id: str, user_id: str):
    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not await class_dao.is_class_member(meeting.class_id, user_id):
        raise HTTPException(status_code=403, detail="You are not a member of this class")

    participant = MeetingParticipant(meeting_id=meeting_id, user_id=user_id)
    await meeting_dao.add_participant(participant)
    return {"success": True, "message": "Successfully joined the meeting"}

async def leave_meeting(meeting_id: str, user_id: str):
    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    await meeting_dao.record_participant_left(meeting_id, user_id)
    return {"success": True, "message": "Successfully left the meeting"}

manager = ConnectionManager()

async def handle_ws_connect(websocket: WebSocket, meeting_id: str, user_id: str) -> str:
    await websocket.accept()

    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        await websocket.close(code=1008, reason="Meeting not found")
        return

    is_member = await class_dao.is_class_member(meeting.class_id, user_id)
    if not is_member:
        await websocket.close(code=1008, reason="Not authorized")
        return

    await manager.connect(websocket, meeting_id, user_id)
    user = await user_dao.find_by_id(user_id)
    username = user.username if user else "Unknown"

    join_msg = {
        "type": "user_joined",
        "user_id": user_id,
        "username": username
    }
    await manager.broadcast(json.dumps(join_msg), meeting_id)
    return username

async def handle_ws_disconnect(meeting_id: str, user_id: str):
    manager.disconnect(meeting_id, user_id)
    await meeting_dao.record_participant_left(meeting_id, user_id)

    leave_msg = {
        "type": "user_left",
        "user_id": user_id
    }
    await manager.broadcast(json.dumps(leave_msg), meeting_id)

async def handle_ws_message(data: dict, meeting_id: str, user_id: str, username: str):
    if data["type"] == "video":
        video_msg = {
            "type": "video",
            "user_id": user_id,
            "data": data["data"]
        }
        await manager.broadcast(json.dumps(video_msg), meeting_id, sender_id=user_id)
