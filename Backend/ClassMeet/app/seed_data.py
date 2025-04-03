from database import get_db
from datetime import datetime, timezone  # Add timezone

db = get_db()

# 1. Drop old collections to refresh
db.users.drop()
db.classes.drop()
db.class_memberships.drop()
db.meetings.drop()
db.meeting_participants.drop()
db.chat_messages.drop()

# 2. Create data for Users
users_data = [
    {"username": "hiep_le", "email": "hiep@example.com", "password": "google-auth"},
    {"username": "tuan_nguyen", "email": "tuan@example.com", "password": "google-auth"},
    {"username": "student1", "email": "student1@example.com", "password": "google-auth"}
]
users_result = db.users.insert_many(users_data)
hiep_id, tuan_id, student1_id = users_result.inserted_ids

# 3. Create data for Classes
classes_data = [
    {"class_name": "Python Programming", "created_by": hiep_id, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
    {"class_name": "Web Development", "created_by": hiep_id, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)}
]
classes_result = db.classes.insert_many(classes_data)
class1_id, class2_id = classes_result.inserted_ids

# 4. Create data for Class_Memberships
class_memberships_data = [
    {"class_id": class1_id, "user_id": hiep_id, "role": "creator", "status": "approved"},
    {"class_id": class1_id, "user_id": tuan_id, "role": "member", "status": "approved"},
    {"class_id": class1_id, "user_id": student1_id, "role": "member", "status": "pending"},
    {"class_id": class2_id, "user_id": hiep_id, "role": "creator", "status": "approved"}
]
db.class_memberships.insert_many(class_memberships_data)

# 5. Create data for Meetings
meetings_data = [
    {"class_id": class1_id, "user_id": hiep_id, "start_time": datetime(2025, 4, 3, 10, 0, 0), "created_at": datetime.now(timezone.utc)},
    {"class_id": class1_id, "user_id": hiep_id, "start_time": datetime(2025, 4, 4, 14, 0, 0), "created_at": datetime.now(timezone.utc)}
]
meetings_result = db.meetings.insert_many(meetings_data)
meeting1_id = meetings_result.inserted_ids[0]

# 6. Create data for Meeting_Participants
meeting_participants_data = [
    {"meeting_id": meeting1_id, "user_id": hiep_id, "joined_at": datetime(2025, 4, 3, 10, 5, 0), "left_at": datetime(2025, 4, 3, 11, 0, 0)},
    {"meeting_id": meeting1_id, "user_id": tuan_id, "joined_at": datetime(2025, 4, 3, 10, 10, 0), "left_at": None}
]
db.meeting_participants.insert_many(meeting_participants_data)

# 7. Create data for Chat_Messages
chat_messages_data = [
    {"meeting_id": meeting1_id, "user_id": hiep_id, "content": "Hello everyone, let's start the meeting!", "sent_at": datetime(2025, 4, 3, 10, 6, 0)},
    {"meeting_id": meeting1_id, "user_id": tuan_id, "content": "Hi, I'm here!", "sent_at": datetime(2025, 4, 3, 10, 11, 0)}
]
db.chat_messages.insert_many(chat_messages_data)

print("Sample data has been successfully inserted!")
