# api/websockets.py
from fastapi import APIRouter, WebSocket
import json
import logging

from management.auth import decode_access_token
from management.meeting_manager import (
    handle_ws_connect,
    handle_ws_disconnect,
    handle_ws_message
)

logger = logging.getLogger(__name__)
websocket_router = APIRouter()

@websocket_router.websocket("/ws/meeting/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str, token: str = None):
    if not token:
        await websocket.close(code=1008, reason="Token required")
        return

    try:
        payload = decode_access_token(token)
        user_id = payload["user_id"]

        # Connect
        username = await handle_ws_connect(websocket, meeting_id, user_id)

        # Listen loop
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            await handle_ws_message(message_data, meeting_id, user_id, username)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        await websocket.close(code=1008, reason="Internal server error")

    finally:
        await handle_ws_disconnect(meeting_id, user_id)
