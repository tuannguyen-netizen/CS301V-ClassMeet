from db_connection import get_db
from datetime import datetime, timezone
from auth import hash_password
import random
import string

db = get_db()

# Function to generate a random class code (6 characters)
def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Drop old collections to start fresh
db.users.drop()
db.classes.drop()
db.class_memberships.drop()
db.meetings.drop()
db.meeting_participants.drop()
db.chat_messages.drop()

# 1. Create sample data for Users
users_data = [
    {"username": "hiep_le", "email": "hiep@example.com", "password": hash_password("password123")},
    {"username": "tuan_nguyen", "email": "tuan@example.com", "password": hash_password("password123")},
    {"username": "student1", "email": "student1@example.com", "password": hash_password("password123")}
]
users_result = db.users.insert_many(users_data)
hiep_id, tuan_id, student1_id = users_result.inserted_ids

# 2. Create sample data for Classes
classes_data = [
    {
        "class_name": "Python Programming",
        "class_code": generate_class_code(),
        "created_by": hiep_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "description": "A class for learning Python programming"
    },
    {
        "class_name": "Web Development",
        "class_code": generate_class_code(),
        "created_by": hiep_id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "description": "A class for learning web development"
    }
]
classes_result = db.classes.insert_many(classes_data)
class1_id, class2_id = classes_result.inserted_ids

# 3. Create sample data for Class Memberships
class_memberships_data = [
    {"class_id": class1_id, "user_id": hiep_id, "role": "creator", "status": "approved"},
    {"class_id": class1_id, "user_id": tuan_id, "role": "member", "status": "approved"},
    {"class_id": class1_id, "user_id": student1_id, "role": "member", "status": "pending"},
    {"class_id": class2_id, "user_id": hiep_id, "role": "creator", "status": "approved"}
]
db.class_memberships.insert_many(class_memberships_data)

# 4. Create sample data for Meetings
meetings_data = [
    {"class_id": class1_id, "user_id": hiep_id, "start_time": datetime(2025, 4, 3, 10, 0, 0), "created_at": datetime.now(timezone.utc)},
    {"class_id": class1_id, "user_id": hiep_id, "start_time": datetime(2025, 4, 4, 14, 0, 0), "created_at": datetime.now(timezone.utc)}
]
meetings_result = db.meetings.insert_many(meetings_data)
meeting1_id = meetings_result.inserted_ids[0]

# 5. Create sample data for Meeting Participants
meeting_participants_data = [
    {"meeting_id": meeting1_id, "user_id": hiep_id, "joined_at": datetime(2025, 4, 3, 10, 5, 0), "left_at": datetime(2025, 4, 3, 11, 0, 0)},
    {"meeting_id": meeting1_id, "user_id": tuan_id, "joined_at": datetime(2025, 4, 3, 10, 10, 0), "left_at": None}
]
db.meeting_participants.insert_many(meeting_participants_data)

# 6. Create sample data for Chat Messages
chat_messages_data = [
    {"meeting_id": meeting1_id, "user_id": hiep_id, "content": "Hello everyone, let's start the meeting!", "sent_at": datetime(2025, 4, 3, 10, 6, 0)},
    {"meeting_id": meeting1_id, "user_id": tuan_id, "content": "Hi, I'm here!", "sent_at": datetime(2025, 4, 3, 10, 11, 0)}
]
db.chat_messages.insert_many(chat_messages_data)

print("Sample data has been inserted successfully!")
