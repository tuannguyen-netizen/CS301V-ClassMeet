# management/class_manager.py
'''from fastapi import HTTPException
from dao.class_dao import ClassDAO
from management.models import ClassCreateRequest, ClassJoinRequest, ClassResponse
from management.models import Class

class_dao = ClassDAO()

async def create_class(data: ClassCreateRequest, user_id: str) -> ClassResponse:
    new_class = Class(
        class_name=data.class_name,
        description=data.description,
        created_by=user_id
    )
    class_id = await class_dao.create_class(new_class)
    created_class = await class_dao.find_by_id(class_id)

    return ClassResponse(
        class_id=created_class.class_id,
        class_name=created_class.class_name,
        description=created_class.description,
        class_code=created_class.class_code,
        created_by=created_class.created_by,
        is_creator=True
    )

async def join_class(data: ClassJoinRequest, user_id: str) -> ClassResponse:
    class_obj = await class_dao.find_by_code(data.class_code)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Invalid class code")

    if await class_dao.is_class_member(class_obj.class_id, user_id):
        raise HTTPException(status_code=400, detail="You are already a member of this class")

    await class_dao.add_member(class_obj.class_id, user_id)
    is_creator = await class_dao.is_class_creator(class_obj.class_id, user_id)

    return ClassResponse(
        class_id=class_obj.class_id,
        class_name=class_obj.class_name,
        description=class_obj.description,
        class_code=class_obj.class_code,
        created_by=class_obj.created_by,
        is_creator=is_creator
    )

async def get_user_classes(user_id: str):
    classes = await class_dao.list_user_classes(user_id)
    result = []
    for cls in classes:
        is_creator = await class_dao.is_class_creator(cls.class_id, user_id)
        result.append(ClassResponse(
            class_id=cls.class_id,
            class_name=cls.class_name,
            description=cls.description,
            class_code=cls.class_code,
            created_by=cls.created_by,
            is_creator=is_creator
        ))
    return result'''


'''# management/class_manager.py
from fastapi import HTTPException
from dao.class_dao import ClassDAO
from dao.user_dao import UserDAO
from management.models import (
    ClassCreateRequest, ClassJoinRequest, ClassResponse,
    ClassMemberResponse, Class
)

class_dao = ClassDAO()
user_dao = UserDAO()

async def create_class(data: ClassCreateRequest, user_id: str) -> ClassResponse:
    new_class = Class(
        class_name=data.class_name,
        description=data.description,
        created_by=user_id
    )
    class_id = await class_dao.create_class(new_class)
    created_class = await class_dao.find_by_id(class_id)

    return ClassResponse(
        class_id=created_class.class_id,
        class_name=created_class.class_name,
        description=created_class.description,
        class_code=created_class.class_code,
        created_by=created_class.created_by,
        is_creator=True
    )

async def join_class(data: ClassJoinRequest, user_id: str) -> ClassResponse:
    class_obj = await class_dao.find_by_code(data.class_code)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Invalid class code")

    if await class_dao.is_class_member(class_obj.class_id, user_id):
        raise HTTPException(status_code=400, detail="You are already a member of this class")

    await class_dao.add_member(class_obj.class_id, user_id)
    is_creator = await class_dao.is_class_creator(class_obj.class_id, user_id)

    return ClassResponse(
        class_id=class_obj.class_id,
        class_name=class_obj.class_name,
        description=class_obj.description,
        class_code=class_obj.class_code,
        created_by=class_obj.created_by,
        is_creator=is_creator
    )

async def get_user_classes(user_id: str):
    classes = await class_dao.list_user_classes(user_id)
    result = []
    for cls in classes:
        is_creator = await class_dao.is_class_creator(cls.class_id, user_id)
        result.append(ClassResponse(
            class_id=cls.class_id,
            class_name=cls.class_name,
            description=cls.description,
            class_code=cls.class_code,
            created_by=cls.created_by,
            is_creator=is_creator
        ))
    return result

async def get_class_members(class_id: str, requester_id: str):
    if not await class_dao.is_class_member(class_id, requester_id):
        raise HTTPException(status_code=403, detail="You are not a member of this class")
    memberships = await class_dao.get_class_members(class_id)
    members = []
    for mem in memberships:
        user = await user_dao.find_by_id(mem["user_id"])
        if user:
            members.append(ClassMemberResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=mem["role"]
            ))
    return members

async def remove_class_member(class_id: str, member_username: str, requester_id: str):
    if not await class_dao.is_class_creator(class_id, requester_id):
        raise HTTPException(status_code=403, detail="Only the class creator can remove members")
    member = await user_dao.find_by_username(member_username)
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    if requester_id == member.user_id:
        raise HTTPException(status_code=400, detail="Creator cannot remove themselves")
    success = await class_dao.remove_member(class_id, member.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found in class")
    return {"success": True, "message": "Member removed"}

async def delete_class(class_id: str, user_id: str):
    if not await class_dao.is_class_creator(class_id, user_id):
        raise HTTPException(status_code=403, detail="Only the class creator can delete the class")
    await class_dao.delete_class(class_id)
    return {"success": True, "message": "Class deleted"}

async def leave_class(class_id: str, user_id: str):
    if await class_dao.is_class_creator(class_id, user_id):
        raise HTTPException(status_code=400, detail="Creator cannot leave their own class")
    success = await class_dao.remove_member(class_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not a member of class")
    return {"success": True, "message": "Left the class"}'''

# management/class_manager.py
from fastapi import HTTPException
from dao.class_dao import ClassDAO
from dao.user_dao import UserDAO
from management.models import (
    ClassCreateRequest, ClassJoinRequest, ClassResponse,
    ClassMemberResponse, Class
)

class_dao = ClassDAO()
user_dao = UserDAO()

async def create_class(data: ClassCreateRequest, user_id: str) -> ClassResponse:
    new_class = Class(
        class_name=data.class_name,
        description=data.description,
        created_by=user_id
    )
    class_id = await class_dao.create_class(new_class)
    created_class = await class_dao.find_by_id(class_id)

    return ClassResponse(
        class_id=created_class.class_id,
        class_name=created_class.class_name,
        description=created_class.description,
        class_code=created_class.class_code,
        created_by=created_class.created_by,
        is_creator=True
    )

async def join_class(data: ClassJoinRequest, user_id: str) -> ClassResponse:
    class_obj = await class_dao.find_by_code(data.class_code)
    if not class_obj:
        raise HTTPException(status_code=404, detail="Invalid class code")

    if await class_dao.is_class_member(class_obj.class_id, user_id):
        raise HTTPException(status_code=400, detail="You are already a member of this class")

    await class_dao.add_member(class_obj.class_id, user_id)
    is_creator = await class_dao.is_class_creator(class_obj.class_id, user_id)

    return ClassResponse(
        class_id=class_obj.class_id,
        class_name=class_obj.class_name,
        description=class_obj.description,
        class_code=class_obj.class_code,
        created_by=class_obj.created_by,
        is_creator=is_creator
    )

async def get_user_classes(user_id: str):
    classes = await class_dao.list_user_classes(user_id)
    result = []
    for cls in classes:
        is_creator = await class_dao.is_class_creator(cls.class_id, user_id)
        result.append(ClassResponse(
            class_id=cls.class_id,
            class_name=cls.class_name,
            description=cls.description,
            class_code=cls.class_code,
            created_by=cls.created_by,
            is_creator=is_creator
        ))
    return result

async def get_class_members(class_id: str, requester_id: str):
    if not await class_dao.is_class_member(class_id, requester_id):
        raise HTTPException(status_code=403, detail="You are not a member of this class")
    memberships = await class_dao.get_class_members(class_id)
    members = []
    for mem in memberships:
        user = await user_dao.find_by_id(mem["user_id"])
        if user:
            members.append(ClassMemberResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=mem["role"]
            ))
    return members

async def remove_class_member(class_id: str, member_username: str, requester_id: str):
    if not await class_dao.is_class_creator(class_id, requester_id):
        raise HTTPException(status_code=403, detail="Only the class creator can remove members")
    member = await user_dao.find_by_username(member_username)
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    if requester_id == member.user_id:
        raise HTTPException(status_code=400, detail="Creator cannot remove themselves")
    success = await class_dao.remove_member(class_id, member.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found in class")
    return {"success": True, "message": "Member removed"}

async def delete_class(class_id: str, user_id: str):
    if not await class_dao.is_class_creator(class_id, user_id):
        raise HTTPException(status_code=403, detail="Only the class creator can delete the class")
    await class_dao.delete_class(class_id)
    return {"success": True, "message": "Class deleted"}

async def leave_class(class_id: str, user_id: str):
    if await class_dao.is_class_creator(class_id, user_id):
        raise HTTPException(status_code=400, detail="Creator cannot leave their own class")
    success = await class_dao.remove_member(class_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not a member of class")
    return {"success": True, "message": "Left the class"}
