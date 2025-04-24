# api/class_api.py
import logging
from fastapi import APIRouter, HTTPException, Depends, Path, Body
from typing import List, Optional
from pydantic import BaseModel, Field

from dao.class_dao import ClassDAO
from dao.user_dao import UserDAO
from utils.models import Class, ClassMembership
from utils.auth import get_current_user
from utils.helpers import format_success_response

logger = logging.getLogger(__name__)
router = APIRouter()
class_dao = ClassDAO()
user_dao = UserDAO()

# Request/Response models
class ClassCreateRequest(BaseModel):
    class_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ClassJoinRequest(BaseModel):
    class_code: str = Field(..., min_length=6, max_length=6)

class ClassResponse(BaseModel):
    class_id: str
    class_name: str
    description: Optional[str]
    class_code: str
    created_by: str
    is_creator: bool

class ClassMemberResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str

@router.post("/create", response_model=ClassResponse)
async def create_class(
        class_data: ClassCreateRequest,
        user_id: str = Depends(get_current_user)
):
    """Create a new class"""
    try:
        # Create new class object
        new_class = Class(
            class_name=class_data.class_name,
            description=class_data.description,
            created_by=user_id
        )

        # Save to database
        class_id = await class_dao.create_class(new_class)

        # Get created class
        created_class = await class_dao.find_by_id(class_id)

        return {
            "class_id": created_class.class_id,
            "class_name": created_class.class_name,
            "description": created_class.description,
            "class_code": created_class.class_code,
            "created_by": created_class.created_by,
            "is_creator": True
        }
    except Exception as e:
        logger.error(f"Error creating class: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error creating class")

@router.post("/join", response_model=ClassResponse)
async def join_class(
        join_data: ClassJoinRequest,
        user_id: str = Depends(get_current_user)
):
    """Join a class using a class code"""
    # Find class by code
    class_obj = await class_dao.find_by_code(join_data.class_code)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Invalid class code")

    # Check if user is already a member
    is_member = await class_dao.is_class_member(class_obj.class_id, user_id)

    if is_member:
        raise HTTPException(status_code=400, detail="You are already a member of this class")

    # Add user to class
    await class_dao.add_member(class_obj.class_id, user_id)

    # Determine user's role
    is_creator = await class_dao.is_class_creator(class_obj.class_id, user_id)

    return {
        "class_id": class_obj.class_id,
        "class_name": class_obj.class_name,
        "description": class_obj.description,
        "class_code": class_obj.class_code,
        "created_by": class_obj.created_by,
        "is_creator": is_creator
    }

@router.get("/my-classes", response_model=List[ClassResponse])
async def get_my_classes(user_id: str = Depends(get_current_user)):
    """Get a list of classes the user is a member of"""
    # Get classes
    classes = await class_dao.list_user_classes(user_id)

    result = []
    for class_obj in classes:
        is_creator = await class_dao.is_class_creator(class_obj.class_id, user_id)
        result.append({
            "class_id": class_obj.class_id,
            "class_name": class_obj.class_name,
            "description": class_obj.description,
            "class_code": class_obj.class_code,
            "created_by": class_obj.created_by,
            "is_creator": is_creator
        })

    return result