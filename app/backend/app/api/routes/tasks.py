from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.task import (
    create_task,
    get_task_by_id,
    get_tasks,
    soft_delete_task,
)
from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
)
def create_task_endpoint(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    return create_task(db, task_data)


@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks_endpoint(
    db: Session = Depends(get_db),
):
    return get_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    task = get_task_by_id(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=204,
)
def delete_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    task = get_task_by_id(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    soft_delete_task(db, task)

    return None
