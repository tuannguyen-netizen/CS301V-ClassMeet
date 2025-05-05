# management/class_manager.py
from fastapi import HTTPException
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
    return result
