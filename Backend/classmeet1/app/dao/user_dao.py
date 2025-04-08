from app.config.database import get_db
from app.models.user import User
from app.utils.auth import hash_password

class UserDAO:
    def __init__(self):
        self.collection = get_db()["users"]

    def create(self, user: User):
        user.password = hash_password(user.password)
        return self.collection.insert_one(user.dict())

    def find_by_email(self, email: str):
        return self.collection.find_one({"email": email})

    def find_by_id(self, user_id: int):
        return self.collection.find_one({"user_id": user_id})

    def update(self, user_id: int, update_data: dict):
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
        return self.collection.update_one({"user_id": user_id}, {"$set": update_data})