from fastapi import APIRouter, Depends
from app.api.controllers import auth_controller, user_controller, class_controller, meeting_controller
from app.utils.auth import verify_jwt_token

router = APIRouter()

# Auth
router.post("/auth/login")(auth_controller.login)
router.post("/auth/logout")(auth_controller.logout)

# User
router.get("/user/me")(user_controller.get_user_info)
router.put("/user/me")(user_controller.update_user_info)

# Class
router.post("/class/create")(class_controller.create_class)
router.post("/class/join")(class_controller.join_class)

# Meeting
router.post("/class/{class_id}/meeting")(meeting_controller.create_meeting)
router.post("/meeting/{meeting_id}/join")(meeting_controller.join_meeting)
router.get("/meeting/{meeting_id}/attendance")(meeting_controller.export_attendance)