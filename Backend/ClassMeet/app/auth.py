from flask import request, jsonify
import jwt
from google_auth_oauthlib.flow import InstalledAppFlow

SECRET_KEY = "your-secret-key"

def google_login():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['openid', 'email', 'profile']
    )
    credentials = flow.run_local_server(port=0)
    return credentials.id_token

def create_token(user_id):
    payload = {"user_id": str(user_id)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.InvalidTokenError:
        return None