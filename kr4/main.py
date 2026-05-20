from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db import get_db
from models import Product
from exceptions import CustomExceptionA, CustomExceptionB, ErrorResponse
from schemas import UserValidate, UserIn, UserOut
import users_storage as storage

app = FastAPI(title="KR4 FastAPI")


# --- 10.1 кастомные исключения ---

@app.exception_handler(CustomExceptionA)
async def handle_exception_a(request: Request, exc: CustomExceptionA):
    print(f"Error A: {exc.message}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error_code="ERR_A", message=exc.message).model_dump(),
    )


@app.exception_handler(CustomExceptionB)
async def handle_exception_b(request: Request, exc: CustomExceptionB):
    print(f"Error B: {exc.message}")
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(error_code="ERR_B", message=exc.message).model_dump(),
    )


@app.get("/check-condition")
async def check_condition(fail: bool = False):
    if fail:
        raise CustomExceptionA("Condition failed")
    return {"ok": True}


@app.get("/resource/{item_id}")
async def get_resource(item_id: int):
    if item_id < 1:
        raise CustomExceptionB(f"Resource {item_id} not found")
    return {"id": item_id, "name": "demo"}


# --- 10.2 валидация ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in err["loc"]),
            "message": err["msg"],
        })
    print(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "errors": errors,
        },
    )


@app.post("/validate-user")
async def validate_user(user: UserValidate):
    return {"message": "User data is valid", "username": user.username}


# --- 9.1 просмотр продуктов из БД ---

@app.get("/products")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "price": p.price,
            "count": p.count,
            "description": p.description,
        }
        for p in products
    ]


# --- 11.1 / 11.2 users API ---

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = storage.next_user_id()
    storage.db[user_id] = user.model_dump()
    return {"id": user_id, **storage.db[user_id]}


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in storage.db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **storage.db[user_id]}


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if storage.db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)
