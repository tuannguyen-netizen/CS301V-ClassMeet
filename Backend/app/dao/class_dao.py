from app.config.database import Database
from app.models.class_ import Class, ClassMembership
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ClassDAO:
    """Data Access Object for Class-related operations"""

    def __init__(self):
        db = Database.get_instance().db
        if db is None:
            logger.error("Database connection is None")
            raise ValueError("Database connection failed")
        self.class_collection = db.classes
        self.membership_collection = db.class_memberships
        if self.class_collection is None or self.membership_collection is None:
            logger.error("Class or membership collection is None")
            raise ValueError("Collections not found")
        logger.info(f"ClassDAO initialized with collections")

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
            # Handle duplicates (unique constraint violations)
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

    async def update_class(self, class_obj):
        """Update a class's information"""
        class_dict = class_obj.to_dict()
        class_id = ObjectId(class_obj.class_id)

        # Remove class_id from the dictionary since we're using _id in MongoDB
        class_dict.pop("class_id", None)

        result = await self.class_collection.update_one(
            {"_id": class_id},
            {"$set": class_dict}
        )
        return result.modified_count > 0

    async def delete_class(self, class_id):
        """Delete a class and all its memberships"""
        # Delete the class
        result = await self.class_collection.delete_one({"_id": ObjectId(class_id)})

        # Delete all memberships for this class
        await self.membership_collection.delete_many({"class_id": class_id})

        return result.deleted_count > 0

    async def list_classes(self, skip=0, limit=100):
        """List classes with pagination"""
        cursor = self.class_collection.find().skip(skip).limit(limit)
        classes = []

        async for class_data in cursor:
            class_data["class_id"] = str(class_data.pop("_id"))
            classes.append(Class.from_dict(class_data))

        return classes

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

    # Membership management methods

    async def add_member(self, class_id, user_id, role=ClassMembership.ROLE_MEMBER,
                         status=ClassMembership.STATUS_APPROVED):
        """Add a user as a member to a class"""
        # Check if the membership already exists
        existing = await self.membership_collection.find_one({
            "class_id": class_id,
            "user_id": user_id
        })

        if existing:
            # If membership exists but status is different, update it
            if existing["status"] != status:
                await self.membership_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"status": status}}
                )
            return str(existing["_id"])

        # Create new membership
        membership = ClassMembership(
            class_id=class_id,
            user_id=user_id,
            role=role,
            status=status
        )

        result = await self.membership_collection.insert_one(membership.to_dict())
        return str(result.inserted_id)

    async def remove_member(self, class_id, user_id):
        """Remove a user from a class"""
        result = await self.membership_collection.delete_one({
            "class_id": class_id,
            "user_id": user_id
        })
        return result.deleted_count > 0

    async def get_class_members(self, class_id):
        """Get all members of a class"""
        cursor = self.membership_collection.find({"class_id": class_id})
        members = []

        async for membership in cursor:
            members.append(ClassMembership.from_dict(membership))

        return members

    async def get_class_creator(self, class_id):
        """Get the creator of a class"""
        creator = await self.membership_collection.find_one({
            "class_id": class_id,
            "role": ClassMembership.ROLE_CREATOR
        })

        if creator:
            return creator["user_id"]
        return None

    async def is_class_member(self, class_id, user_id):
        """Check if a user is a member of a class"""
        membership = await self.membership_collection.find_one({
            "class_id": class_id,
            "user_id": user_id,
            "status": ClassMembership.STATUS_APPROVED
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