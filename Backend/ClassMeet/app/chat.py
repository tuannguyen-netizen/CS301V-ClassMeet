import asyncio
import websockets
import json
from db_connection import get_db
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

# Use asyncio.run() to start the WebSocket server
async def main():
    server = await websockets.serve(handle_chat, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
