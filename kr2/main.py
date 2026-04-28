from fastapi import FastAPI, HTTPException, Response, Request, Depends, Cookie, Header
from fastapi.responses import JSONResponse
from typing import Optional, Annotated
from datetime import datetime, timezone
import time
import uuid

from models import UserCreate, LoginData, CommonHeaders
from database import sample_products, valid_sessions, session_data
from security import (
    generate_session_token, generate_signed_token, verify_signed_token,
    generate_session_token_v3, verify_session_token_v3, verify_credentials
)

app = FastAPI(
    title="FastAPI Контрольная работа",
    description="Решение заданий 3.1, 3.2, 5.1, 5.2, 5.3, 5.4, 5.5",
    version="1.0.0"
)


@app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    return user


@app.get("/product/{product_id}")
async def get_product(product_id: int):
    for product in sample_products:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products/search")
async def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10
):
    results = []
    
    for product in sample_products:
        if category and product["category"].lower() != category.lower():
            continue
        
        if keyword.lower() in product["name"].lower():
            results.append(product)
    
    return results[:limit]


@app.post("/login")
async def login(response: Response, login_data: LoginData):
    if not verify_credentials(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_token = generate_session_token()
    
    valid_sessions[session_token] = login_data.username
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=300,  
        secure=False  
    )
    
    return {"message": "Login successful", "username": login_data.username}


@app.get("/user")
async def get_user_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token or session_token not in valid_sessions:
        return JSONResponse(
            status_code=401,
            content={"message": "Unauthorized"}
        )
    
    username = valid_sessions[session_token]
    return {"username": username, "message": "Profile information"}


@app.post("/login_v2")
async def login_v2(response: Response, login_data: LoginData):
    if not verify_credentials(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(uuid.uuid4())
    
    signed_token = generate_signed_token(user_id)
    
    session_data[user_id] = {
        "username": login_data.username,
        "last_activity": time.time()
    }
    
    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        max_age=300,
        secure=False
    )
    
    return {"message": "Login successful", "user_id": user_id}


@app.get("/profile")
async def get_profile(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    user_id = verify_signed_token(session_token)
    
    if not user_id or user_id not in session_data:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    user_info = session_data[user_id]
    return {
        "user_id": user_id,
        "username": user_info["username"],
        "message": "Profile information (signed cookie)"
    }


SESSION_TIMEOUT = 300  
EXTEND_THRESHOLD = 180 


@app.post("/login_v3")
async def login_v3(response: Response, login_data: LoginData):
    """
    Маршрут входа с динамической сессией (задание 5.3)
    """
    if not verify_credentials(login_data.username, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(uuid.uuid4())
    current_time = int(time.time())
    
    token = generate_session_token_v3(user_id, current_time)
    
    session_data[user_id] = {
        "username": login_data.username,
        "last_activity": current_time
    }
    
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=SESSION_TIMEOUT,
        secure=False
    )
    
    return {"message": "Login successful", "user_id": user_id, "timestamp": current_time}


@app.get("/profile_v3")
async def get_profile_v3(response: Response, session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return JSONResponse(status_code=401, content={"message": "Session expired"})
    
    user_id, token_timestamp = verify_session_token_v3(session_token)
    
    if not user_id or user_id not in session_data:
        return JSONResponse(status_code=401, content={"message": "Invalid session"})
    
    current_time = int(time.time())
    last_activity = session_data[user_id]["last_activity"]
    time_since_last = current_time - last_activity
    
    if time_since_last > SESSION_TIMEOUT:
        del session_data[user_id]
        return JSONResponse(status_code=401, content={"message": "Session expired"})
    
    if token_timestamp != last_activity:
        return JSONResponse(status_code=401, content={"message": "Invalid session"})
    
    should_extend = time_since_last >= EXTEND_THRESHOLD
    
    if should_extend:
        new_timestamp = current_time
        new_token = generate_session_token_v3(user_id, new_timestamp)
        
        session_data[user_id]["last_activity"] = new_timestamp
        
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            max_age=SESSION_TIMEOUT,
            secure=False
        )
        
        return {
            "user_id": user_id,
            "username": session_data[user_id]["username"],
            "message": "Session extended",
            "time_since_last": time_since_last
        }
    
    return {
        "user_id": user_id,
        "username": session_data[user_id]["username"],
        "message": "Profile information",
        "time_since_last": time_since_last,
        "session_extended": False
    }


@app.get("/headers")
async def get_headers(headers: CommonHeaders = Depends()):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


@app.get("/info")
async def get_info(response: Response, headers: CommonHeaders = Depends()):
    current_time = datetime.now(timezone.utc).isoformat(timespec='seconds')
    response.headers["X-Server-Time"] = current_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }


@app.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        for user_id, data in list(session_data.items()):
            if data.get("session_token") == session_token:
                del session_data[user_id]
        
        for token, username in list(valid_sessions.items()):
            if token == session_token:
                del valid_sessions[token]
    
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}