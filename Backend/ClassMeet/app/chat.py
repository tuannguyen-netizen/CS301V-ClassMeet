import asyncio
import websockets
import json
from database import get_db
from datetime import datetime, timezone
from bson import ObjectId

db = get_db()

async def handle_chat(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        chat_data = {
            "meeting_id": ObjectId(data["meeting_id"]),
            "user_id": ObjectId(data["user_id"]),
            "content": data["content"],
            "sent_at": datetime.now(timezone.utc)
        }
        db.chat_messages.insert_one(chat_data)
        await websocket.send(json.dumps({"message": data["content"], "user_id": data["user_id"]}))

start_server = websockets.serve(handle_chat, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()