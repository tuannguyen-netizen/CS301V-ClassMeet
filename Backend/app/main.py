import uvicorn
import logging
import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.video_server import VideoCallServer  # Note: Adjusted import path

from app.api.routes import router
from app.config.database import initialize_db, Database
from app.config.settings import DEBUG, HOST, PORT
from app.utils.helpers import format_error_response

# Configure logging
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="ClassMeet API",
    description="API for ClassMeet application - A platform for managing classes and online meetings",
    version="1.0.0",
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://classmeet.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=format_error_response("Server error occurred", 500)
    )


# Register API router
app.include_router(router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# Global variable to hold the video server instance
video_server = None
server_thread = None


# Define lifespan for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global video_server, server_thread

    # Startup code
    logger.info("Starting application")
    try:
        db = await initialize_db()
        logger.info("Successfully connected to MongoDB database")
    except Exception as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        raise

    # Start the video server in a separate thread
    video_server = VideoCallServer(host='0.0.0.0', port=5000)
    server_thread = threading.Thread(target=video_server.start, daemon=True)
    server_thread.start()
    logger.info("Video call server started in a separate thread")

    yield

    # Shutdown code
    logger.info("Shutting down application")

    # Stop the video server (close socket and clients)
    if video_server:
        video_server.server_socket.close()
        for client in video_server.clients:
            try:
                client.close()
            except:
                pass
        logger.info("Video call server stopped")

    # Close database connection
    try:
        Database.get_instance().close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}", exc_info=True)


# Assign the lifespan to the app after defining it
app.lifespan = lifespan


# Run application
def run():
    """Run FastAPI application with Uvicorn"""
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )


if __name__ == "__main__":
    run()