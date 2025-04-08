from flask import Flask, request, jsonify, send_file
from db_connection import get_db
from auth import create_token, verify_token, authenticate_user, hash_password
from datetime import datetime, timezone
import pandas as pd
import io
from bson import ObjectId

app = Flask(__name__)
db = get_db()

# Register account
@app.route('/auth/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    username = request.json.get('username')

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    # Check if email already exists
    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    # Hash password and save user to database
    hashed_password = hash_password(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_password
    }
    result = db.users.insert_one(user_data)
    user_id = result.inserted_id

    # Generate token for user
    token = create_token(user_id)
    return jsonify({"token": token, "expiresIn": 3600})

# Login
@app.route('/auth/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Authenticate user
    user_id = authenticate_user(email, password)
    if not user_id:
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate token
    token = create_token(user_id)
    return jsonify({"token": token, "expiresIn": 3600})

# Logout
@app.route('/auth/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Logout successful"}), 200

# Get current user info
@app.route('/user/me', methods=['GET'])
def get_user_info():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "userId": str(user["_id"]),
        "name": user["username"],
        "email": user["email"],
        "role": "user"  # Can be updated if roles system is implemented
    })

# Update user info
@app.route('/user/me', methods=['PUT'])
def update_user_info():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    name = request.json.get('name')
    email = request.json.get('email')

    update_data = {}
    if name:
        update_data["username"] = name
    if email:
        if db.users.find_one({"email": email, "_id": {"$ne": ObjectId(user_id)}}):
            return jsonify({"error": "Email already exists"}), 400
        update_data["email"] = email

    if not update_data:
        return jsonify({"error": "No data to update"}), 400

    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return jsonify({
        "userId": str(user["_id"]),
        "name": user["username"],
        "email": user["email"],
        "role": "user"
    })

# Create a class
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

# Add a member
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

# Join a class
@app.route('/class/join', methods=['POST'])
def join_class():
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    class_code = request.json.get('classCode')
    if not class_code or len(class_code) != 6:
        return jsonify({"error": "Invalid class code"}), 400

    class_info = db.classes.find_one({"class_code": class_code})
    if not class_info:
        return jsonify({"error": "Class not found"}), 404

    membership = {
        "class_id": class_info["_id"],
        "user_id": ObjectId(user_id),
        "role": "member",
        "status": "pending"
    }
    db.class_memberships.insert_one(membership)
    return jsonify({
        "classId": str(class_info["_id"]),
        "className": class_info["class_name"],
        "description": class_info.get("description", ""),
        "teacherId": str(class_info["created_by"])
    })

# Create a meeting
@app.route('/class/<class_id>/meeting', methods=['POST'])
def create_meeting(class_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Only class creator can start a meeting
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

# Join a meeting
@app.route('/meeting/<meeting_id>/join', methods=['POST'])
def join_meeting(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    # User must be an approved member to join
    if not db.class_memberships.find_one({"class_id": meeting["class_id"], "user_id": ObjectId(user_id), "status": "approved"}):
        return jsonify({"error": "User not authorized to join this meeting"}), 403

    participant_data = {
        "meeting_id": ObjectId(meeting_id),
        "user_id": ObjectId(user_id),
        "joined_at": datetime.now(timezone.utc)
    }
    db.meeting_participants.insert_one(participant_data)
    return jsonify({"message": f"User {user_id} joined meeting {meeting_id}"})

# Leave a meeting
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

# End a meeting
@app.route('/meeting/<meeting_id>/end', methods=['POST'])
def end_meeting(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    # Only meeting creator can end it
    if meeting["user_id"] != ObjectId(user_id):
        return jsonify({"error": "Only the meeting creator can end it"}), 403

    db.meetings.update_one({"_id": ObjectId(meeting_id)}, {"$set": {"end_time": datetime.now(timezone.utc)}})
    db.meeting_participants.update_many(
        {"meeting_id": ObjectId(meeting_id), "left_at": None},
        {"$set": {"left_at": datetime.now(timezone.utc)}}
    )
    return jsonify({"message": f"Meeting {meeting_id} ended"})

# Export attendance data
@app.route('/meeting/<meeting_id>/attendance', methods=['GET'])
def export_attendance(meeting_id):
    token = request.headers.get('Authorization').split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    meeting = db.meetings.find_one({"_id": ObjectId(meeting_id)})
    # Only meeting creator can export attendance
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
