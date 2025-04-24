# api/websockets.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import json
import logging
from typing import Dict, List

from dao.meeting_dao import MeetingDAO
from dao.user_dao import UserDAO
from dao.class_dao import ClassDAO
from utils.models import ChatMessage
from utils.auth import decode_access_token

logger = logging.getLogger(__name__)

websocket_router = APIRouter()
meeting_dao = MeetingDAO()
user_dao = UserDAO()
class_dao = ClassDAO()


# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, meeting_id: str, user_id: str):
        await websocket.accept()
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = {}
        self.active_connections[meeting_id][user_id] = websocket
        logger.info(f"User {user_id} connected to meeting {meeting_id}")

    def disconnect(self, meeting_id: str, user_id: str):
        if meeting_id in self.active_connections and user_id in self.active_connections[meeting_id]:
            del self.active_connections[meeting_id][user_id]
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
            logger.info(f"User {user_id} disconnected from meeting {meeting_id}")

    async def broadcast(self, message: str, meeting_id: str, sender_id: str = None):
        if meeting_id in self.active_connections:
            for user_id, connection in self.active_connections[meeting_id].items():
                if sender_id is None or user_id != sender_id:
                    await connection.send_text(message)


manager = ConnectionManager()


@websocket_router.websocket("/ws/meeting/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str, token: str = None):
    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    try:
        # Authenticate user
        payload = decode_access_token(token)
        user_id = payload["user_id"]

        # Verify meeting exists
        meeting = await meeting_dao.find_by_id(meeting_id)
        if not meeting:
            await websocket.close(code=1008, reason="Meeting not found")
            return

        # Verify user is a member of the class
        is_member = await class_dao.is_class_member(meeting.class_id, user_id)
        if not is_member:
            await websocket.close(code=1008, reason="Not authorized to join this meeting")
            return

        # Connect to WebSocket
        await manager.connect(websocket, meeting_id, user_id)

        # Get user info
        user = await user_dao.find_by_id(user_id)
        username = user.username if user else "Unknown User"

        # Notify others that user joined
        join_message = {
            "type": "user_joined",
            "user_id": user_id,
            "username": username
        }
        await manager.broadcast(json.dumps(join_message), meeting_id)

        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Handle different message types
                if message_data["type"] == "chat":
                    # Create message object
                    message = ChatMessage(
                        meeting_id=meeting_id,
                        user_id=user_id,
                        content=message_data["content"]
                    )

                    # Save to database
                    message_id = await meeting_dao.add_chat_message(message)

                    # Broadcast to all participants
                    chat_message = {
                        "type": "chat",
                        "message_id": message_id,
                        "user_id": user_id,
                        "username": username,
                        "content": message_data["content"],
                        "sent_at": message.sent_at.isoformat()
                    }
                    await manager.broadcast(json.dumps(chat_message), meeting_id)

                elif message_data["type"] == "video":
                    # Just relay video data to other participants
                    video_message = {
                        "type": "video",
                        "user_id": user_id,
                        "data": message_data["data"]
                    }
                    await manager.broadcast(json.dumps(video_message), meeting_id, user_id)

        except WebSocketDisconnect:
            # Handle disconnect
            manager.disconnect(meeting_id, user_id)

            # Record participant left
            await meeting_dao.record_participant_left(meeting_id, user_id)

            # Notify others that user left
            leave_message = {
                "type": "user_left",
                "user_id": user_id,
                "username": username
            }
            await manager.broadcast(json.dumps(leave_message), meeting_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        await websocket.close(code=1008, reason="Internal server error")