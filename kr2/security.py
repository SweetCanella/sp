import uuid
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timezone
from typing import Optional, Tuple
import time


SECRET_KEY = "key"
serializer = URLSafeTimedSerializer(SECRET_KEY)


def generate_session_token() -> str:
    return str(uuid.uuid4())


def generate_signed_token(user_id: str) -> str:
    return serializer.dumps(user_id)


def verify_signed_token(token: str) -> Optional[str]:
    try:
        user_id = serializer.loads(token, max_age=300) 
        return user_id
    except (SignatureExpired, BadSignature):
        return None


def generate_timestamped_token(user_id: str, timestamp: int) -> str:
    data = f"{user_id}.{timestamp}"
    signature = serializer.dumps(data)
    return f"{user_id}.{timestamp}.{signature.split('.')[-1]}"


def generate_session_token_v3(user_id: str, timestamp: int) -> str:
    data = f"{user_id}.{timestamp}"
    signed_data = serializer.dumps(data)
    parts = signed_data.split('.')
    signature = parts[-1] if len(parts) > 1 else signed_data
    return f"{user_id}.{timestamp}.{signature}"


def verify_session_token_v3(token: str) -> Tuple[Optional[str], Optional[int]]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None, None
        
        user_id, timestamp_str, provided_signature = parts
        
        data = f"{user_id}.{timestamp_str}"
        expected_data = serializer.loads(f"{data}.{provided_signature}")
        
        if expected_data != data:
            return None, None
        
        timestamp = int(timestamp_str)
        return user_id, timestamp
        
    except (SignatureExpired, BadSignature, ValueError, IndexError):
        return None, None


def verify_credentials(username: str, password: str) -> bool:
    valid_users = {
        "user123": "password123",
        "alice": "alice123",
        "admin": "admin123"
    }
    return valid_users.get(username) == password