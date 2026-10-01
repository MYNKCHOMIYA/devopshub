from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate

from datetime import datetime, timezone

def create_project(db: Session, project_data: ProjectCreate) -> Project:
    project = Project(
        owner_id=project_data.owner_id,
        name=project_data.name,
        description=project_data.description,
        status=project_data.status,
        priority=project_data.priority,
        start_date=project_data.start_date,
        due_date=project_data.due_date,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_project_by_id(
    db: Session,
    project_id: UUID,
) -> Project | None:
    statement = select(Project).where(
        Project.id == project_id,
        Project.deleted_at.is_(None),
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def get_projects(db: Session) -> list[Project]:
    statement = select(Project).where(
        Project.deleted_at.is_(None),
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def soft_delete_project(
    db: Session,
    project: Project,
) -> Project:
    project.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    return project
