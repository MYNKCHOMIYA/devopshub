from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.project import create_project, get_project_by_id,get_projects,soft_delete_project
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=201,
)
def create_project_endpoint(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    return create_project(db, project_data)


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_projects_endpoint(
    db: Session = Depends(get_db),
):
    return get_projects(db)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return project

@router.delete(
    "/{project_id}",
    status_code=204,
)
def delete_project_endpoint(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    soft_delete_project(
        db,
        project,
        project.owner_id,
    )

    return None
