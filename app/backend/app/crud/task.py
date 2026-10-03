from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


def create_task(db: Session, task_data: TaskCreate) -> Task:
    task = Task(
        project_id=task_data.project_id,
        created_by_id=task_data.created_by_id,
        assignee_id=task_data.assignee_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
    )

    db.add(task)

    try:
        db.commit()
        db.refresh(task)
    except IntegrityError:
        db.rollback()
        raise

    return task


def get_task_by_id(
    db: Session,
    task_id: UUID,
) -> Task | None:
    statement = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None),
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_tasks(db: Session) -> list[Task]:
    statement = select(Task).where(
        Task.deleted_at.is_(None),
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def soft_delete_task(
    db: Session,
    task: Task,
) -> Task:
    task.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return task
