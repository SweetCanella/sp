from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import MODE
from database import (
    fake_users_db,
    demo_items,
    get_db_connection,
    create_tables,
)
import database as db_module

from models import (
    UserInDB,
    UserRegister,
    LoginData,
    TodoCreate,
    TodoUpdate,
)
from security import (
    auth_user,
    verify_docs_credentials,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_roles,
    check_permission,
    get_password_hash,
    find_user_by_username,
)

docs_basic = HTTPBasic(auto_error=False)

# отключаем стандартную документацию, добавим свою (задание 6.3)
app = FastAPI(
    title="KR3 FastAPI",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def startup():
    create_tables()
    # тестовый пользователь для basic-auth
    if "admin" not in fake_users_db:
        fake_users_db["admin"] = {
            "hashed_password": get_password_hash("secret"),
            "role": "admin",
        }


# --- документация (6.3) ---

def _check_docs_access(credentials: Optional[HTTPBasicCredentials]):
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    verify_docs_credentials(credentials)


@app.get("/docs", include_in_schema=False)
async def custom_docs(credentials: Optional[HTTPBasicCredentials] = Depends(docs_basic)):
    _check_docs_access(credentials)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="KR3 API")


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(credentials: Optional[HTTPBasicCredentials] = Depends(docs_basic)):
    _check_docs_access(credentials)
    return JSONResponse(app.openapi())


@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    if MODE == "PROD":
        raise HTTPException(status_code=404, detail="Not Found")
    raise HTTPException(status_code=404, detail="Not Found")


# --- задание 6.1 / 6.2: basic auth ---

@app.get("/login")
async def login_basic(user: UserInDB = Depends(auth_user)):
    return {"message": f"Welcome, {user.username}!"}


# --- задание 6.2 / 6.5 / 7.1: регистрация в памяти ---

@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def register_user(request: Request, user: UserRegister):
    if find_user_by_username(user.username) is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    role = user.role if user.role in ("admin", "user", "guest") else "user"

    fake_users_db[user.username] = {
        "hashed_password": get_password_hash(user.password),
        "role": role,
    }

    # задание 8.1: также пишем в SQLite (пароль открытым текстом)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, user.password),
    )
    conn.commit()
    conn.close()

    return {"message": "New user created"}


# --- задание 6.4 / 6.5: JWT ---

@app.post("/login")
@limiter.limit("5/minute")
async def login_jwt(request: Request, data: LoginData):
    user_data = find_user_by_username(data.username)

    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not authenticate_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Authorization failed")

    token = create_access_token(data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
async def protected_resource(current_user: dict = Depends(require_roles("admin", "user"))):
    return {"message": "Access granted", "username": current_user["username"]}


# --- задание 7.1: RBAC эндпоинты ---

@app.post("/admin/items")
async def admin_create_item(
    title: str,
    description: str,
    current_user: dict = Depends(require_roles("admin")),
):
    global next_item_id
    item_id = db_module.next_item_id
    db_module.next_item_id += 1
    demo_items[item_id] = {
        "id": item_id,
        "title": title,
        "description": description,
    }
    return {"message": "Item created", "item": demo_items[item_id]}


@app.get("/items/{item_id}")
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
    if not check_permission(current_user["role"], "read"):
        raise HTTPException(status_code=403, detail="Access denied")

    if item_id not in demo_items:
        raise HTTPException(status_code=404, detail="Item not found")

    return demo_items[item_id]


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    title: str,
    description: str,
    current_user: dict = Depends(get_current_user),
):
    if not check_permission(current_user["role"], "update"):
        raise HTTPException(status_code=403, detail="Access denied")

    if item_id not in demo_items:
        raise HTTPException(status_code=404, detail="Item not found")

    demo_items[item_id]["title"] = title
    demo_items[item_id]["description"] = description
    return demo_items[item_id]


@app.delete("/items/{item_id}")
async def delete_item(item_id: int, current_user: dict = Depends(require_roles("admin"))):
    if item_id not in demo_items:
        raise HTTPException(status_code=404, detail="Item not found")

    del demo_items[item_id]
    return {"message": "Item deleted"}


# --- задание 8.2: CRUD Todo ---

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (todo.title, todo.description),
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": False,
    }


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "completed": bool(row["completed"]),
    }


@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id),
    )
    conn.commit()
    conn.close()

    return {
        "id": todo_id,
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed,
    }


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    conn.commit()
    conn.close()
    return {"message": "Todo deleted successfully"}
