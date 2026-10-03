from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.activity import (
    create_activity,
    get_activities_for_project,
    get_activities_for_task,
    get_activity_by_id,
)
from app.db.session import get_db
from app.schemas.activity import ActivityCreate, ActivityResponse


router = APIRouter(
    prefix="/activities",
    tags=["activities"],
)


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=201,
)
def create_activity_endpoint(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
):
    return create_activity(db, activity_data)


@router.get(
    "/project/{project_id}",
    response_model=list[ActivityResponse],
)
def get_project_activities_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    return get_activities_for_project(db, project_id)


@router.get(
    "/task/{task_id}",
    response_model=list[ActivityResponse],
)
def get_task_activities_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    return get_activities_for_task(db, task_id)


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
)
def get_activity_endpoint(
    activity_id: UUID,
    db: Session = Depends(get_db),
):
    activity = get_activity_by_id(db, activity_id)

    if activity is None:
        raise HTTPException(
            status_code=404,
            detail="Activity not found.",
        )

    return activity
