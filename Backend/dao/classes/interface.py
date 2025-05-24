from pydantic import BaseModel, Field

class ClassCreateRequest(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)

class ClassJoinRequest(BaseModel):
    class_code: str

class ClassResponse(BaseModel):
    class_id: str
    class_name: str
    description: str
    class_code: str
    created_by: str

class ClassMemberResponse(BaseModel):
    user_id: str