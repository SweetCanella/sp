from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_current_user, get_storage
from app.schemas import TaskCreate, TaskOut, StatusUpdate, TaskStatus, User
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task_id = storage.next_id()
    data = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "owner_id": user.id,
    }
    storage.tasks[task_id] = data
    return data


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = None,
    min_priority: Optional[int] = Query(default=None, ge=1, le=5),
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    result = []
    for task in storage.tasks.values():
        if task["owner_id"] != user.id:
            continue
        if status is not None and task["status"] != status:
            continue
        if min_priority is not None and task["priority"] < min_priority:
            continue
        result.append(task)
    return result


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.tasks.get(task_id)
    if task is None or task["owner_id"] != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(
    task_id: int,
    payload: StatusUpdate,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.tasks.get(task_id)
    if task is None or task["owner_id"] != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = payload.status
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.tasks.get(task_id)
    if task is None or task["owner_id"] != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    del storage.tasks[task_id]
    return Response(status_code=204)
