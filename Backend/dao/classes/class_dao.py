import logging
from bson import ObjectId
from fastapi import HTTPException
from dao.db_config import Database
from dao.classes.object import Class
from dao.classes.class_interface import ClassDAOInterface

logger = logging.getLogger(__name__)

class ClassDAO(ClassDAOInterface):
    def __init__(self):
        self.db = Database.get_instance().db
        self.collection = self.db.classes
        logger.info("ClassDAO initialized")

    async def create_class(self, class_obj):
        class_dict = class_obj.to_dict()
        result = await self.collection.insert_one(class_dict)
        return str(result.inserted_id)

    async def find_by_id(self, class_id):
        class_data = await self.collection.find_one({"_id": ObjectId(class_id)})
        if class_data:
            class_data["class_id"] = str(class_data.pop("_id"))
            return Class.from_dict(class_data)
        return None

    async def find_by_class_code(self, class_code):
        class_data = await self.collection.find_one({"class_code": class_code})
        if class_data:
            class_data["class_id"] = str(class_data.pop("_id"))
            return Class.from_dict(class_data)
        return None

    async def add_user_to_class(self, class_id: str, user_id: str):
        membership = {
            "class_id": class_id,
            "user_id": user_id,
            "joined_at": datetime.utcnow()
        }
        try:
            await self.db.class_memberships.insert_one(membership)
        except Exception as e:
            if "duplicate key error" in str(e):
                raise HTTPException(status_code=400, detail="User already in class")
            raise e

    async def get_class_members(self, class_id: str):
        memberships = await self.db.class_memberships.find({"class_id": class_id}).to_list(None)
        return [{"user_id": m["user_id"]} for m in memberships]

    async def get_user_memberships(self, user_id: str):
        memberships = await self.db.class_memberships.find({"user_id": user_id}).to_list(None)
        return [{"class_id": m["class_id"]} for m in memberships]

    async def remove_user_from_class(self, class_id: str, user_id: str):
        result = await self.db.class_memberships.delete_one({"class_id": class_id, "user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not in class")

    async def delete_class(self, class_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(class_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Class not found")
        await self.db.class_memberships.delete_many({"class_id": class_id})