from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.schemas.activity import ActivityCreate


def create_activity(
    db: Session,
    activity_data: ActivityCreate,
) -> Activity:
    activity = record_activity(db, activity_data)
    db.commit()
    db.refresh(activity)

    return activity


def get_activity_by_id(
    db: Session,
    activity_id: UUID,
) -> Activity | None:
    statement = select(Activity).where(
        Activity.id == activity_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_activities_for_project(
    db: Session,
    project_id: UUID,
) -> list[Activity]:
    statement = (
        select(Activity)
        .where(Activity.project_id == project_id)
        .order_by(Activity.created_at)
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def get_activities_for_task(
    db: Session,
    task_id: UUID,
) -> list[Activity]:
    statement = (
        select(Activity)
        .where(Activity.task_id == task_id)
        .order_by(Activity.created_at)
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def record_activity(
    db: Session,
    activity_data: ActivityCreate,
) -> Activity:
    activity = Activity(
        project_id=activity_data.project_id,
        task_id=activity_data.task_id,
        actor_id=activity_data.actor_id,
        action=activity_data.action,
        activity_metadata=activity_data.metadata,
    )

    db.add(activity)

    return activity
