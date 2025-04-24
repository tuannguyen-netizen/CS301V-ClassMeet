# main.py
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.auth_api import router as auth_router
from api.user_api import router as user_router
from api.class_api import router as class_router
from api.meeting_api import router as meeting_router
from api.websockets import websocket_router
from dao.db_config import initialize_db

# Load settings from .env
import os
from dotenv import load_dotenv
load_dotenv()

# Server Configuration
DEBUG = os.getenv('DEBUG', 'False') == 'True'
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')

# Configure logging
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define lifespan for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    logger.info("Starting application")
    await initialize_db()
    logger.info("Database initialized")
    yield
    # Shutdown code
    logger.info("Shutting down application")

# Initialize FastAPI app
app = FastAPI(
    title="ClassMeet API",
    description="API for ClassMeet application",
    version="1.0.0",
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://classmeet.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/user", tags=["User Management"])
app.include_router(class_router, prefix="/api/class", tags=["Class Management"])
app.include_router(meeting_router, prefix="/api/meeting", tags=["Meeting Management"])
app.include_router(websocket_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )