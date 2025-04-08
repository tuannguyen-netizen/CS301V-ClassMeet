import jwt
import bcrypt
from db_connection import get_db

SECRET_KEY = "your-secret-key"
db = get_db()

def hash_password(password):
    """Hash the password before storing it in the database."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Check if the user's input password matches the hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_token(user_id):
    """Generate a JWT token for the user."""
    payload = {"user_id": str(user_id)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """Verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.InvalidTokenError:
        return None

def authenticate_user(email, password):
    """Authenticate a user using email and password."""
    user = db.users.find_one({"email": email})
    if user and verify_password(password, user["password"]):
        return user["_id"]
    return None
