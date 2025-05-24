from dao.db_config import Database
from bson import ObjectId
from dao.user.user_interface import UserDAOInterface
from dao.user.object import User
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class UserDAO(UserDAOInterface):
    def __init__(self):
        self.db = Database.get_instance().db
        self.collection = self.db.users
        logger.info("UserDAO initialized")

    async def create_user(self, user):
        user_dict = user.to_db_dict()
        try:
            result = await self.collection.insert_one(user_dict)
            return str(result.inserted_id)
        except Exception as e:
            if "duplicate key error" in str(e) and "email" in str(e):
                raise HTTPException(status_code=400, detail="Email already exists")
            elif "duplicate key error" in str(e) and "username" in str(e):
                raise HTTPException(status_code=400, detail="Username already exists")
            raise e

    async def find_by_id(self, user_id):
        user_data = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None

    async def find_by_email(self, email):
        user_data = await self.collection.find_one({"email": email})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None

    async def find_by_username(self, username):
        user_data = await self.collection.find_one({"username": username})
        if user_data:
            user_data["user_id"] = str(user_data.pop("_id"))
            return User.from_dict(user_data)
        return None