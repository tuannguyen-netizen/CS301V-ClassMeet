from fastapi import Depends, HTTPException
from app.dao.meeting_dao import MeetingDAO
from app.dao.class_dao import ClassDAO
from app.models.meeting import Meeting, MeetingParticipant, ChatMessage
from app.utils.auth import verify_jwt_token  # Đảm bảo import
from app.utils.helpers import export_to_csv
from datetime import datetime


def create_meeting(class_id: int, meeting_data: Meeting, token: str = Depends(verify_jwt_token)):
    class_dao = ClassDAO()
    meeting_dao = MeetingDAO()

    class_ = class_dao.find_by_id(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    if class_["created_by"] != token["sub"]:
        raise HTTPException(status_code=403, detail="Only class leader can create meetings")

    meeting_data.class_id = class_id
    meeting_data.user_id = token["sub"]
    meeting_dao.create(meeting_data)
    return {"meeting_id": meeting_data.meeting_id, "message": "Meeting created"}


def join_meeting(meeting_id: int, token: str = Depends(verify_jwt_token)):
    meeting_dao = MeetingDAO()
    meeting = meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    participant = MeetingParticipant(user_id=token["sub"])
    meeting_dao.add_participant(meeting_id, participant.dict())
    return {"message": "Joined meeting"}


def export_attendance(meeting_id: int, token: str = Depends(verify_jwt_token)):
    meeting_dao = MeetingDAO()
    meeting = meeting_dao.find_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    participants = meeting_dao.get_participants(meeting_id)
    data = [{"user_id": p["user_id"], "joined_at": p["joined_at"].isoformat()} for p in participants]
    filename = f"attendance_{meeting_id}.csv"
    return export_to_csv(data, filename)