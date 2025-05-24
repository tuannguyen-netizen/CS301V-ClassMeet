from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
import os

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/classmeet")

class Database:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def __init__(self):
        if Database._client is None:
            try:
                self._client = AsyncIOMotorClient(MONGODB_URI)
                db_name = MONGODB_URI.split("/")[-1].split("?")[0] or "classmeet"
                self._db = self._client[db_name]
                logger.info(f"Connected to MongoDB database: {db_name}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    @property
    def db(self):
        return self._db

    def close(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
            self._client = None
            self._db = None

async def initialize_db():
    db = Database.get_instance().db
    collections = ["users", "classes", "class_memberships", "meetings", "meeting_participants", "chat_messages"]
    for collection_name in collections:
        collection_names = await db.list_collection_names()
        if collection_name not in collection_names:
            await db.create_collection(collection_name)

    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("username", unique=True)
        await db.classes.create_index("class_code", unique=True)
        await db.class_memberships.create_index([("class_id", 1), ("user_id", 1)], unique=True)
        await db.meeting_participants.create_index([("meeting_id", 1), ("user_id", 1)], unique=True)
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")

    return db