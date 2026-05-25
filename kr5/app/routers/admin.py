from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import require_admin, get_storage
from app.schemas import User
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats(_: User = Depends(require_admin), storage: TaskStorage = Depends(get_storage)):
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for task in storage.tasks.values():
        by_status[task["status"]] = by_status.get(task["status"], 0) + 1
    return {
        "total_tasks": len(storage.tasks),
        "by_status": by_status,
    }


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(
    task_id: int,
    _: User = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
):
    if task_id not in storage.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del storage.tasks[task_id]
    return Response(status_code=204)
