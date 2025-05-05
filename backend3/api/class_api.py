# api/class_api.py
from fastapi import APIRouter, Depends
from typing import List
from management.auth import get_current_user
from management.models import ClassCreateRequest, ClassJoinRequest, ClassResponse
from management.class_manager import create_class, join_class, get_user_classes

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
