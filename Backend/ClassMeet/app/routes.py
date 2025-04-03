from flask import Flask, request, jsonify, send_file
from database import get_db
from auth import create_token, verify_token
from datetime import datetime, timezone
import pandas as pd
import io
from bson import ObjectId

app = Flask(__name__)
db = get_db()

# Google Login
@app.route('/auth/login', methods=['POST'])
def login():
    token = google_login()
    email = request.json['email']
    user = db.users.find_one({"email": email})
    if not user:
        user_data = {
            "username": email.split('@')[0],
            "email": email,
            "password": "google-auth"
        }
        result = db.users.insert_one(user_data)
        user_id = result.inserted_id
    else:
        user_id = user["_id"]
    token = create_token(user_id)
    return jsonify({"token": token, "expiresIn": 3600})

# Create Class
@app.route('/class/create', methods=['POST'])
def create_class():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    class_data = {
        "class_name": request.json['class_name'],
        "created_by": ObjectId(user_id),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    result = db.classes.insert_one(class_data)
    class_id = result.inserted_id

    db.class_memberships.insert_one({
        "class_id": class_id,
        "user_id": ObjectId(user_id),
        "role": "creator",
        "status": "approved"
    })

    return jsonify({"class_id": str(class_id), "class_name": request.json['class_name']})

# Add Member
@app.route('/class/<class_id>/members', methods=['POST'])
def add_member(class_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    membership = {
        "class_id": ObjectId(class_id),
        "user_id": ObjectId(request.json['user_id']),
        "role": "member",
        "status": "pending"
    }
    db.class_memberships.insert_one(membership)
    return jsonify({"message": "Member added, pending approval"})

# Create Meeting
@app.route('/class/<class_id>/meeting', methods=['POST'])
def create_meeting(class_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    membership = db.class_memberships.find_one({"class_id": ObjectId(class_id), "user_id": ObjectId(user_id)})
    if not membership or membership["role"] != "creator":
        return jsonify({"error": "Only the class creator can start a meeting"}), 403

    meeting_data = {
        "class_id": ObjectId(class_id),
        "user_id": ObjectId(user_id),
        "start_time": datetime.strptime(request.json['start_time'], "%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now(timezone.utc)
    }
    result = db.meetings.insert_one(meeting_data)
    return jsonify({"meeting_id": str(result.inserted_id), "class_id": class_id})

# Join Meeting
@app.route('/meeting/<meeting_id>/join', methods=['POST'])
def join_meeting(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    if not db.class_memberships.find_one({"class_id": meeting["class_id"], "user_id": ObjectId(user_id), "status": "approved"}):
        return jsonify({"error": "User not authorized to join this meeting"}), 403

    participant_data = {
        "meeting_id": ObjectId(meeting_id),
        "user_id": ObjectId(user_id),
        "joined_at": datetime.now(timezone.utc)
    }
    db.meeting_participants.insert_one(participant_data)
    return jsonify({"message": f"User {user_id} joined meeting {meeting_id}"})

# Leave Meeting
@app.route('/meeting/<meeting_id>/leave', methods=['POST'])
def leave_meeting(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db.meeting_participants.update_one(
        {"meeting_id": ObjectId(meeting_id), "user_id": ObjectId(user_id), "left_at": None},
        {"$set": {"left_at": datetime.now(timezone.utc)}}
    )
    return jsonify({"message": f"User {user_id} left meeting {meeting_id}"})

# End Meeting
@app.route('/meeting/<meeting_id>/end', methods=['POST'])
def end_meeting(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    if meeting["user_id"] != ObjectId(user_id):
        return jsonify({"error": "Only the meeting creator can end it"}), 403

    db.meetings.update_one({"_id": ObjectId(meeting_id)}, {"$set": {"end_time": datetime.now(timezone.utc)}})
    db.meeting_participants.update_many(
        {"meeting_id": ObjectId(meeting_id), "left_at": None},
        {"$set": {"left_at": datetime.now(timezone.utc)}}
    )
    return jsonify({"message": f"Meeting {meeting_id} ended"})

# Export Attendance Data
@app.route('/meeting/<meeting_id>/attendance', methods=['GET'])
def export_attendance(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    if meeting["user_id"] != ObjectId(user_id):
        return jsonify({"error": "Only the meeting creator can export attendance"}), 403

    participants = db.meeting_participants.find({"meeting_id": ObjectId(meeting_id)})
    data = []
    for p in participants:
        user = db.users.find_one({"_id": p["user_id"]})
        data.append({
            "Username": user["username"],
            "Joined At": p["joined_at"],
            "Left At": p.get("left_at")
        })

    df = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f"attendance_meeting_{meeting_id}.csv"
    )
