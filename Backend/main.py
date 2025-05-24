from fastapi import FastAPI, Depends
from api.user.auth_api import router as auth_router
from api.user.user_api import router as user_router
from api.classes.class_api import router as class_router
from api.meeting.meeting_api import router as meeting_router
from dao.user.interface import UserRegistrationRequest, UserLoginRequest
from management.management import register_user, login_user
from management.auth import get_current_user
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(class_router, prefix="/api/class", tags=["Class"])
app.include_router(meeting_router, prefix="/api/meeting", tags=["Meeting"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to ClassMeet API!"}

# Current user info
@app.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host=host, port=port)