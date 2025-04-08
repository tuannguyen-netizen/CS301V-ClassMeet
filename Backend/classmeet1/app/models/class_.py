from pydantic import BaseModel
from datetime import datetime
from typing import List

class ClassMember(BaseModel):
    user_id: int
    role: str  # "leader" hoặc "member"
    status: str  # "pending" hoặc "approved"

class Class(BaseModel):
    class_id: int
    class_name: str
    created_by: int  # user_id của leader
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    members: List[ClassMember] = []