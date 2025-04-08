from fastapi import Depends, HTTPException
from app.dao.class_dao import ClassDAO
from app.models.class_ import Class, ClassMember
from app.utils.auth import verify_jwt_token  # Đảm bảo import


def create_class(class_data: Class, token: str = Depends(verify_jwt_token)):
    dao = ClassDAO()
    class_data.created_by = token["sub"]
    class_data.members = [ClassMember(user_id=token["sub"], role="leader", status="approved")]
    dao.create(class_data)
    return {"class_id": class_data.class_id, "message": "Class created"}


def join_class(class_id: int, token: str = Depends(verify_jwt_token)):
    dao = ClassDAO()
    class_ = dao.find_by_id(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")

    member = ClassMember(user_id=token["sub"], role="member", status="pending")
    dao.add_member(class_["class_id"], member.dict())
    return {"class_id": class_["class_id"], "message": "Joined class"}