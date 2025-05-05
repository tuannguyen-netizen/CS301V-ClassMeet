import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load secret key and token expiration from .env
SECRET_KEY = os.getenv('SECRET_KEY', 'classmeet_secret_key')
JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 3600))  # 1 hour default

# Print secret key to ensure correct loading (for debugging)
print("🧩 Loaded SECRET_KEY:", SECRET_KEY)

# Set up FastAPI security scheme
security = HTTPBearer()


def create_access_token(user_id: str) -> str:
    """
    Create a JWT token for a given user ID.
    :param user_id: The ID of the authenticated user
    :return: Encoded JWT token string
    """
    now = datetime.now(timezone.utc)
    exp_time = now + timedelta(seconds=JWT_EXPIRATION)

    payload = {
        "user_id": user_id,
        "iat": int(now.timestamp()),       # Issued At
        "exp": int(exp_time.timestamp())   # Expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    :param token: Encoded JWT string
    :return: Decoded payload dictionary
    :raises: HTTPException if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(f"✅ PAYLOAD after decode: {payload}")  # Debug payload
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    FastAPI dependency to extract user ID from token in Authorization header.
    :param credentials: Bearer token passed in header
    :return: user_id string
    :raises: HTTPException if token is missing or invalid
    """
    token = credentials.credentials

    # Debug: print the token received
    print(f"🔐 Received Token: {token}")

    # Decode the token to get payload
    payload = decode_access_token(token)

    # Debug: print decoded payload
    print(f"✅ Decoded Payload: {payload}")

    return payload["user_id"]
