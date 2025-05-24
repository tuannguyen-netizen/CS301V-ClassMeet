from fastapi import APIRouter, Depends, HTTPException
from typing import List
from management.auth import get_current_user
from dao.classes.interface import ClassCreateRequest, ClassJoinRequest, ClassResponse, ClassMemberResponse  # Changed 'class' to 'classes'
from management.management import create_class, join_class, get_user_classes
from dao.classes.class_dao import ClassDAO  # Changed 'class' to 'classes'

router = APIRouter()
class_dao = ClassDAO()

@router.post("/create", response_model=ClassResponse)
async def create(class_data: ClassCreateRequest, user_id: str = Depends(get_current_user)):
    return await create_class(class_data, user_id)

@router.post("/join", response_model=ClassResponse)
async def join(join_data: ClassJoinRequest, user_id: str = Depends(get_current_user)):
    return await join_class(join_data, user_id)

@router.get("/my-classes", response_model=List[ClassResponse])
async def my_classes(user_id: str = Depends(get_current_user)):
    return await get_user_classes(user_id)

@router.get("/{class_id}/members", response_model=List[ClassMemberResponse])
async def members(class_id: str, user_id: str = Depends(get_current_user)):
    members = await class_dao.get_class_members(class_id)
    return [ClassMemberResponse(user_id=member["user_id"]) for member in members]

@router.delete("/{class_id}/members/{member_id}")
async def remove_member(class_id: str, member_id: str, user_id: str = Depends(get_current_user)):
    class_obj = await class_dao.find_by_id(class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    if class_obj.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only class creator can remove members")
    await class_dao.remove_user_from_class(class_id, member_id)
    return {"message": "Member removed successfully"}

@router.delete("/{class_id}")
async def delete(class_id: str, user_id: str = Depends(get_current_user)):
    class_obj = await class_dao.find_by_id(class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    if class_obj.created_by != user_id:
        raise HTTPException(status_code=403, detail="Only class creator can delete class")
    await class_dao.delete_class(class_id)
    return {"message": "Class deleted successfully"}

@router.post("/{class_id}/leave")
async def leave(class_id: str, user_id: str = Depends(get_current_user)):
    class_obj = await class_dao.find_by_id(class_id)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    await class_dao.remove_user_from_class(class_id, user_id)
    return {"message": "User left class successfully"}