import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server Configuration
DEBUG = os.getenv('DEBUG', 'False') == 'True'
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_not_for_production')

# JWT Configuration
JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))  # Default: 1 hour

# Verify required environment variables
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

if SECRET_KEY == 'default_secret_key_not_for_production' and not DEBUG:
    raise ValueError("SECRET_KEY must be set in production environment")