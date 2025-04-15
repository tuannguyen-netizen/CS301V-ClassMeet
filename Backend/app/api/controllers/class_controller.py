from fastapi import APIRouter, HTTPException, Depends, Path, Body
from typing import List, Optional
from pydantic import BaseModel, Field

from app.dao.class_dao import ClassDAO
from app.dao.user_dao import UserDAO
from app.models.class_ import Class, ClassMembership
from app.utils.auth import get_current_user
from app.utils.helpers import format_success_response

router = APIRouter()
class_dao = ClassDAO()
user_dao = UserDAO()


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


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class_details(
        class_id: str = Path(...),
        user_id: str = Depends(get_current_user)
):
    """Get details of a class"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has permission to view class details
    is_member = await class_dao.is_class_member(class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this class")

    # Determine user's role
    is_creator = await class_dao.is_class_creator(class_id, user_id)

    return {
        "class_id": class_obj.class_id,
        "class_name": class_obj.class_name,
        "description": class_obj.description,
        "class_code": class_obj.class_code,
        "created_by": class_obj.created_by,
        "is_creator": is_creator
    }


@router.get("/{class_id}/members", response_model=List[ClassMemberResponse])
async def get_class_members(
        class_id: str = Path(...),
        user_id: str = Depends(get_current_user)
):
    """Get a list of class members"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has permission to view members
    is_member = await class_dao.is_class_member(class_id, user_id)

    if not is_member:
        raise HTTPException(status_code=403, detail="You are not a member of this class")

    # Get members
    memberships = await class_dao.get_class_members(class_id)

    result = []
    for membership in memberships:
        # Get user details
        member = await user_dao.find_by_id(membership.user_id)
        if member:
            result.append({
                "user_id": member.user_id,
                "username": member.username,
                "email": member.email,
                "role": membership.role
            })

    return result


@router.post("/{class_id}/members")
async def add_class_member(
        class_id: str = Path(...),
        email: str = Body(..., embed=True),
        user_id: str = Depends(get_current_user)
):
    """Add a member to a class by email"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has permission to add members (only creator)
    is_creator = await class_dao.is_class_creator(class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can add members")

    # Find user by email
    member = await user_dao.find_by_email(email)

    if not member:
        raise HTTPException(status_code=404, detail="User with this email not found")

    # Check if user is already a member
    is_already_member = await class_dao.is_class_member(class_id, member.user_id)

    if is_already_member:
        raise HTTPException(status_code=400, detail="User is already a member of this class")

    # Add user to class
    await class_dao.add_member(class_id, member.user_id)

    return format_success_response(message="Member added to class successfully")


@router.delete("/{class_id}/members/{member_id}")
async def remove_class_member(
        class_id: str = Path(...),
        member_id: str = Path(...),
        user_id: str = Depends(get_current_user)
):
    """Remove a member from a class"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has permission to remove members (only creator)
    is_creator = await class_dao.is_class_creator(class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can remove members")

    # Check if member exists in class
    is_member = await class_dao.is_class_member(class_id, member_id)

    if not is_member:
        raise HTTPException(status_code=404, detail="User is not a member of this class")

    # Check if trying to remove class creator (self)
    is_member_creator = await class_dao.is_class_creator(class_id, member_id)

    if is_member_creator:
        raise HTTPException(status_code=400, detail="Cannot remove the class creator from the class")

    # Remove member from class
    await class_dao.remove_member(class_id, member_id)

    return format_success_response(message="Member removed from class successfully")


@router.delete("/{class_id}")
async def delete_class(
        class_id: str = Path(...),
        user_id: str = Depends(get_current_user)
):
    """Delete a class"""
    # Check if class exists
    class_obj = await class_dao.find_by_id(class_id)

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    # Check if user has permission to delete class (only creator)
    is_creator = await class_dao.is_class_creator(class_id, user_id)

    if not is_creator:
        raise HTTPException(status_code=403, detail="Only the class creator can delete the class")

    # Delete class
    await class_dao.delete_class(class_id)

    return format_success_response(message="Class deleted successfully")