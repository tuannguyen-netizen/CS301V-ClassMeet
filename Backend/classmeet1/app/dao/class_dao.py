from app.config.database import get_db
from app.models.class_ import Class

class ClassDAO:
    def __init__(self):
        self.collection = get_db()["classes"]

    def create(self, class_: Class):
        return self.collection.insert_one(class_.dict())

    def find_by_id(self, class_id: int):
        return self.collection.find_one({"class_id": class_id})

    def add_member(self, class_id: int, member: dict):
        return self.collection.update_one(
            {"class_id": class_id},
            {"$push": {"members": member}}
        )