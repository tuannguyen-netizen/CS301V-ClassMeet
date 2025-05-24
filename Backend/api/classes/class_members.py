from fastapi import APIRouter, Depends, HTTPException
from typing import List
from management.auth import get_current_user
from dao.classes.interface import ClassMemberResponse  # Changed 'class' to 'classes'
from dao.classes.class_dao import ClassDAO  # Changed 'class' to 'classes'

router = APIRouter()
class_dao = ClassDAO()

@router.get("/", response_model=List[ClassMemberResponse])
async def get_class_members(class_id: str, user_id: str = Depends(get_current_user)):
    class_obj = await class_dao.find_by_id(class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    members = await class_dao.get_class_members(class_id)
    return [ClassMemberResponse(user_id=member["user_id"]) for member in members]