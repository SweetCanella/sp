import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, DOCS_USER, DOCS_PASSWORD
from database import fake_users_db
from models import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

basic_security = HTTPBasic()
bearer_security = HTTPBearer()

ROLE_PERMISSIONS = {
    "admin": {"create", "read", "update", "delete"},
    "user": {"read", "update"},
    "guest": {"read"},
}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def find_user_by_username(username: str) -> Optional[dict]:
    for db_username, user_data in fake_users_db.items():
        if secrets.compare_digest(db_username, username):
            return user_data
    return None


def auth_user(credentials: HTTPBasicCredentials = Depends(basic_security)) -> UserInDB:
    user_data = find_user_by_username(credentials.username)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not verify_password(credentials.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )

    return UserInDB(username=credentials.username, hashed_password=user_data["hashed_password"])


def verify_docs_credentials(credentials: HTTPBasicCredentials) -> str:
    login_ok = secrets.compare_digest(credentials.username, DOCS_USER)
    pass_ok = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not (login_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def authenticate_user(username: str, password: str) -> bool:
    user_data = find_user_by_username(username)
    if user_data is None:
        return False
    return verify_password(password, user_data["hashed_password"])


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_security)) -> dict:
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_data = find_user_by_username(username)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"username": username, "role": user_data.get("role", "user")}


def require_roles(*allowed_roles: str):
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user

    return checker


def check_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
