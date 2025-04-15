from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

from app.config.settings import MONGODB_URI

# Configure logging
logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern to ensure only one database connection is created"""
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def __init__(self):
        """Initialize database connection"""
        if Database._client is None:
            try:
                # Connect to MongoDB using AsyncIOMotorClient
                self._client = AsyncIOMotorClient(MONGODB_URI)

                # Get database name from connection string (or default to 'classmeet')
                db_name = MONGODB_URI.split('/')[-1].split('?')[0] or 'classmeet'
                self._db = self._client[db_name]

                logger.info(f"Connected to MongoDB database: {db_name}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    @property
    def db(self):
        """Get the database instance"""
        return self._db

    def close(self):
        """Close the database connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
            self._client = None
            self._db = None


# Create collections and indexes on startup
async def initialize_db():
    """Initialize database collections and indexes"""
    db = Database.get_instance().db

    # Create collections if they don't exist
    collections = ['users', 'classes', 'class_memberships', 'meetings', 'meeting_participants', 'chat_messages']
    for collection_name in collections:
        collection_names = await db.list_collection_names()
        if collection_name not in collection_names:
            await db.create_collection(collection_name)

    # Create indexes safely
    try:
        await db.users.create_index('email', unique=True)
        await db.users.create_index('username', unique=True)

        await db.classes.create_index('class_code', unique=True)

        await db.class_memberships.create_index([('class_id', 1), ('user_id', 1)], unique=True)

        await db.meeting_participants.create_index([('meeting_id', 1), ('user_id', 1)], unique=True)
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")
        # Continue execution even if there was an issue with indexes

    return db