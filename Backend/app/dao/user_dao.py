from app.config.database import Database
from app.models.user import User
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class UserDAO:
    """Data Access Object for User-related operations"""

    def __init__(self):
        db = Database.get_instance().db
        if db is None:
            logger.error("Database connection is None")
            raise ValueError("Database connection failed")
        self.collection = db.users
        if self.collection is None:
            logger.error("Users collection is None")
            raise ValueError("Users collection not found")
        logger.info(f"UserDAO initialized with collection: {self.collection.name}")

    async def create_user(self, user):
        """Create a new user in the database"""
        user_dict = user.to_db_dict()
        try:
            result = await self.collection.insert_one(user_dict)
            return str(result.inserted_id)
        except Exception as e:
            # Handle duplicates (unique constraint violations)
            if "duplicate key error" in str(e):
                if "email" in str(e):
                    raise ValueError("Email already exists")
                elif "username" in str(e):
                    raise ValueError("Username already exists")
            raise e

    async def find_by_id(self, user_id):
        """Find a user by their ID"""
        user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None

    async def find_by_email(self, email):
        """Find a user by their email"""
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None

    async def find_by_username(self, username):
        """Find a user by their username"""
        user_data = await self.collection.find_one({"username": username})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None

    async def update_user(self, user):
        """Update a user's information"""
        user_dict = user.to_db_dict()
        user_id = ObjectId(user.user_id)

        # Remove user_id from the dictionary since we're using _id in MongoDB
        user_dict.pop("user_id", None)

        result = await self.collection.update_one(
            {"_id": user_id},
            {"$set": user_dict}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id):
        """Delete a user from the database"""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def list_users(self, skip=0, limit=100):
        """List users with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []

        async for user_data in cursor:
            user_data["user_id"] = str(user_data.pop("_id"))
            users.append(User.from_dict(user_data))

        return users