import os

from fastapi import FastAPI

from app.routers import tasks, users, admin, ws

app = FastAPI(title="KR5 FastAPI")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(ws.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV", "local")}
