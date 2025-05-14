# api/class_api.py
from fastapi import APIRouter, Depends
from typing import List
from management.auth import get_current_user
from management.models import ClassCreateRequest
from management.models import ClassJoinRequest, ClassResponse
from management.class_manager import create_class, join_class, get_user_classes
from management.models import ClassMemberResponse

from management.class_manager import (
    create_class, join_class, get_user_classes,
    get_class_members, remove_class_member,
    delete_class, leave_class
)

router = APIRouter()

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
    return await get_class_members(class_id, user_id)

@router.delete("/{class_id}/members/{member_id}")
async def remove_member(class_id: str, member_id: str, user_id: str = Depends(get_current_user)):
    return await remove_class_member(class_id, member_id, user_id)

@router.delete("/{class_id}")
async def delete(class_id: str, user_id: str = Depends(get_current_user)):
    return await delete_class(class_id, user_id)

@router.post("/{class_id}/leave")
async def leave(class_id: str, user_id: str = Depends(get_current_user)):
    return await leave_class(class_id, user_id)


'''@router.post("/create", response_model=ClassResponse)
async def create(
    class_data: ClassCreateRequest,
    user_id: str = Depends(get_current_user)
):
    return await create_class(class_data, user_id)


@router.post("/join", response_model=ClassResponse)
async def join(
    join_data: ClassJoinRequest,
    user_id: str = Depends(get_current_user)
):
    return await join_class(join_data, user_id)


@router.get("/my-classes", response_model=List[ClassResponse])
async def my_classes(user_id: str = Depends(get_current_user)):
    return await get_user_classes(user_id)'''
