from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate
from app.schemas.activity import ActivityCreate


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
        # Flush the Task INSERT without committing.
        # This makes task.id available for the audit record.
        db.flush()

        from app.crud.activity import record_activity

        record_activity(
            db,
            ActivityCreate(
                project_id=task.project_id,
                task_id=task.id,
                actor_id=task.created_by_id,
                action="TASK_CREATED",
                metadata={
                    "title": task.title,
                },
            ),
        )

        db.commit()
        db.refresh(task)

    except IntegrityError:
        db.rollback()
        raise

    return task


def update_task_status(
    db: Session,
    task: Task,
    new_status: TaskStatus,
    actor_id: UUID,
) -> Task:
    old_status = task.status
    new_status_value = new_status.value

    # Nothing changed, so there is nothing to audit.
    if old_status == new_status_value:
        return task

    task.status = new_status_value

    # Flush the Task UPDATE without committing.
    # The Task change and Activity record must share
    # the same database transaction.
    db.flush()

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=task.project_id,
            task_id=task.id,
            actor_id=actor_id,
            action="TASK_STATUS_CHANGED",
            metadata={
                "old_status": old_status,
                "new_status": new_status_value,
            },
        ),
    )

    db.commit()
    db.refresh(task)

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
    actor_id: UUID,
) -> Task:
    # A task that is already soft-deleted should not
    # generate another TASK_DELETED audit event.
    if task.deleted_at is not None:
        return task

    task.deleted_at = datetime.now(timezone.utc)

    # Flush the soft delete without committing.
    # The deletion and audit record must share the
    # same database transaction.
    db.flush()

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=task.project_id,
            task_id=task.id,
            actor_id=actor_id,
            action="TASK_DELETED",
            metadata={
                "title": task.title,
            },
        ),
    )

    db.commit()
    db.refresh(task)

    return task

def update_task_assignee(
    db: Session,
    task: Task,
    new_assignee_id: UUID,
    actor_id: UUID,
) -> Task:
    old_assignee_id = task.assignee_id

    # Nothing changed, so there is nothing to audit.
    if old_assignee_id == new_assignee_id:
        return task

    task.assignee_id = new_assignee_id

    # Flush the Task UPDATE without committing.
    # The assignment change and audit record must share
    # the same database transaction.
    db.flush()

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=task.project_id,
            task_id=task.id,
            actor_id=actor_id,
            action="TASK_ASSIGNED",
            metadata={
                "old_assignee_id": str(old_assignee_id),
                "new_assignee_id": str(new_assignee_id),
            },
        ),
    )

    db.commit()
    db.refresh(task)

    return task
