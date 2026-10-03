from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.activity import ActivityCreate
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

    # Flush sends the INSERT without committing the transaction.
    # This makes project.id available for the audit record.
    db.flush()

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=project.id,
            task_id=None,
            actor_id=project.owner_id,
            action="PROJECT_CREATED",
            metadata={
                "name": project.name,
            },
        ),
    )

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
    actor_id: UUID,
) -> Project:
    # A project that is already soft-deleted should not
    # generate another PROJECT_DELETED audit event.
    if project.deleted_at is not None:
        return project

    project.deleted_at = datetime.now(timezone.utc)

    # Flush the soft delete without committing.
    # The deletion and audit record must share the
    # same database transaction.
    db.flush()

    from app.crud.activity import record_activity

    record_activity(
        db,
        ActivityCreate(
            project_id=project.id,
            task_id=None,
            actor_id=actor_id,
            action="PROJECT_DELETED",
            metadata={
                "name": project.name,
            },
        ),
    )

    db.commit()
    db.refresh(project)

    return project
