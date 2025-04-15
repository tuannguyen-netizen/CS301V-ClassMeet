from fastapi import APIRouter

from app.api.controllers import auth_controller, user_controller, class_controller, meeting_controller

# Create main router
router = APIRouter()

# Register routers for each controller
router.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
router.include_router(user_controller.router, prefix="/user", tags=["User Management"])
router.include_router(class_controller.router, prefix="/class", tags=["Class Management"])
router.include_router(meeting_controller.router, prefix="", tags=["Meeting Management"])