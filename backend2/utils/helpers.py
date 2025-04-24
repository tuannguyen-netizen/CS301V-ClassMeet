# utils/helpers.py
import re
from fastapi import HTTPException


def validate_email(email):
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email


def validate_password(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return password


def validate_username(username):
    """Validate username."""
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Username may only contain letters, numbers, and underscores")
    return username


def format_success_response(data=None, message=None):
    """Format success response consistently."""
    response = {"success": True}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return response