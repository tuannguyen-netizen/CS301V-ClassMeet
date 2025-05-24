from pydantic import BaseModel, Field

class MeetingCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    class_id: str
    start_time: str
    end_time: str

class MeetingResponse(BaseModel):
    meeting_id: str
    title: str
    class_id: str
    created_by: str
    start_time: str
    end_time: str | None