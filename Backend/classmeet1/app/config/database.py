from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        client.admin.command("ping")
        print("Kết nối MongoDB thành công!")
        return db
    except Exception as e:
        print(f"Lỗi kết nối MongoDB: {e}")
        raise