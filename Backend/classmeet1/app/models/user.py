from pydantic import BaseModel, EmailStr

class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    password: str  # Lưu dưới dạng hashed