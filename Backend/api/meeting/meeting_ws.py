from fastapi import APIRouter, WebSocket, Depends, HTTPException
from management.auth import get_current_user
from dao.meeting.meeting_dao import MeetingDAO
from bson import ObjectId
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
meeting_dao = MeetingDAO()

@router.websocket("/{meeting_id}/chat")
async def meeting_chat(websocket: WebSocket, meeting_id: str, user_id: str = Depends(get_current_user)):
    meeting = await meeting_dao.find_by_id(meeting_id)
    if not meeting:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        async def store_message(message: str):
            await meeting_dao.db.chat_messages.insert_one({
                "meeting_id": meeting_id,
                "user_id": user_id,
                "message": message,
                "timestamp": datetime.utcnow()
            })

        async def broadcast(message: str):
            participants = await meeting_dao.get_meeting_participants(meeting_id)
            for participant in participants:
                await websocket.send_text(f"{user_id}: {message}")

        while True:
            data = await websocket.receive_text()
            await store_message(data)
            await broadcast(data)
    except Exception as e:
        logger.error(f"WebSocket error in meeting {meeting_id}: {e}")
        await websocket.close()