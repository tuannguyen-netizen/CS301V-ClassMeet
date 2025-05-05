# dao/class_dao.py
import logging
from bson import ObjectId
from dao.db_config import Database
from management.models import Class, ClassMembership


logger = logging.getLogger(__name__)


class ClassDAO:
    """Data Access Object for Class-related operations"""

    def __init__(self):
        db = Database.get_instance().db
        self.class_collection = db.classes
        self.membership_collection = db.class_memberships
        logger.info("ClassDAO initialized")

    async def create_class(self, class_obj):
        """Create a new class in the database"""
        class_dict = class_obj.to_dict()

        try:
            # Insert the class
            result = await self.class_collection.insert_one(class_dict)
            class_id = str(result.inserted_id)

            # Create membership for the creator
            membership = ClassMembership(
                class_id=class_id,
                user_id=class_obj.created_by,
                role=ClassMembership.ROLE_CREATOR
            )

            await self.membership_collection.insert_one(membership.to_dict())

            return class_id
        except Exception as e:
            # Handle duplicates
            if "duplicate key error" in str(e) and "class_code" in str(e):
                raise ValueError("Class code already exists")
            raise e

    async def find_by_id(self, class_id):
        """Find a class by its ID"""
        class_data = await self.class_collection.find_one({"_id": ObjectId(class_id)})
        if class_data:
            class_data["class_id"] = str(class_data.pop("_id"))
            return Class.from_dict(class_data)
        return None

    async def find_by_code(self, class_code):
        """Find a class by its code"""
        class_data = await self.class_collection.find_one({"class_code": class_code})
        if class_data:
            class_data["class_id"] = str(class_data.pop("_id"))
            return Class.from_dict(class_data)
        return None

    async def list_user_classes(self, user_id):
        """List all classes that a user is a member of"""
        # Find all memberships for this user
        cursor = self.membership_collection.find({"user_id": user_id})

        class_ids = []
        async for membership in cursor:
            class_ids.append(membership["class_id"])

        if not class_ids:
            return []

        # Find all classes that match these IDs
        classes = []
        cursor = self.class_collection.find({"_id": {"$in": [ObjectId(cid) for cid in class_ids]}})

        async for class_data in cursor:
            class_data["class_id"] = str(class_data.pop("_id"))
            classes.append(Class.from_dict(class_data))

        return classes

    async def add_member(self, class_id, user_id, role=ClassMembership.ROLE_MEMBER):
        """Add a user as a member to a class"""
        # Check if the membership already exists
        existing = await self.membership_collection.find_one({
            "class_id": class_id,
            "user_id": user_id
        })

        if existing:
            return str(existing["_id"])

        # Create new membership
        membership = ClassMembership(
            class_id=class_id,
            user_id=user_id,
            role=role
        )

        result = await self.membership_collection.insert_one(membership.to_dict())
        return str(result.inserted_id)

    async def is_class_member(self, class_id, user_id):
        """Check if a user is a member of a class"""
        membership = await self.membership_collection.find_one({
            "class_id": class_id,
            "user_id": user_id
        })
        return membership is not None

    async def is_class_creator(self, class_id, user_id):
        """Check if a user is the creator of a class"""
        membership = await self.membership_collection.find_one({
            "class_id": class_id,
            "user_id": user_id,
            "role": ClassMembership.ROLE_CREATOR
        })
        return membership is not None