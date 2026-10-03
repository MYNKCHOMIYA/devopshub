import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from app.core.security import hash_password
from app.crud.activity import get_activities_for_project
from app.crud.project import (
    create_project,
    get_project_by_id,
    get_projects,
    soft_delete_project,
)
from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate


def test_create_project():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None

    try:
        user = User(
            username=f"projectowner_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project_data = ProjectCreate(
            owner_id=user.id,
            name="DevOpsHub Project",
            description="Production-grade task management platform",
        )

        project = create_project(db, project_data)

        assert project.id is not None
        assert project.owner_id == user.id
        assert project.name == "DevOpsHub Project"
        assert project.description == "Production-grade task management platform"

    finally:
        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_project_by_id():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None

    try:
        user = User(
            username=f"projectreader_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project Reader",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project_data = ProjectCreate(
            owner_id=user.id,
            name="Read Test Project",
        )

        project = create_project(db, project_data)

        found_project = get_project_by_id(db, project.id)

        assert found_project is not None
        assert found_project.id == project.id
        assert found_project.owner_id == user.id
        assert found_project.name == "Read Test Project"

    finally:
        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_projects():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project_one = None
    project_two = None

    try:
        user = User(
            username=f"projectlist_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project List User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project_one = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Project One",
            ),
        )

        project_two = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Project Two",
            ),
        )

        projects = get_projects(db)

        project_ids = {project.id for project in projects}

        assert project_one.id in project_ids
        assert project_two.id in project_ids

    finally:
        if project_one is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project_one.id
                )
            )
            db.delete(project_one)
            db.commit()

        if project_two is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project_two.id
                )
            )
            db.delete(project_two)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_projects_excludes_deleted_projects():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    active_project = None
    deleted_project = None

    try:
        user = User(
            username=f"projectsoftdelete_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project Soft Delete User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        active_project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Active Project",
            ),
        )

        deleted_project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Deleted Project",
            ),
        )

        deleted_project.deleted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(deleted_project)

        projects = get_projects(db)

        project_ids = {project.id for project in projects}

        assert active_project.id in project_ids
        assert deleted_project.id not in project_ids

    finally:
        if active_project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == active_project.id
                )
            )
            db.delete(active_project)
            db.commit()

        if deleted_project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == deleted_project.id
                )
            )
            db.delete(deleted_project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_soft_delete_project():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None

    try:
        user = User(
            username=f"projectdelete_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project Delete User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Project To Delete",
            ),
        )

        deleted_project = soft_delete_project(
            db,
            project,
            user.id,
        )

        assert deleted_project.deleted_at is not None
        assert isinstance(deleted_project.deleted_at, datetime)
        assert deleted_project.deleted_at.tzinfo is not None

        found_project = get_project_by_id(db, project.id)

        assert found_project is None

    finally:
        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_create_project_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None

    try:
        user = User(
            username=f"activity_project_{unique_value}",
            email=f"activity_project_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Activity Project Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project_data = ProjectCreate(
            owner_id=user.id,
            name="Activity Test Project",
            description="Project activity test",
        )

        project = create_project(db, project_data)

        activities = get_activities_for_project(
            db,
            project.id,
        )

        assert len(activities) == 1

        activity = activities[0]

        assert activity.project_id == project.id
        assert activity.task_id is None
        assert activity.actor_id == user.id
        assert activity.action == "PROJECT_CREATED"
        assert activity.activity_metadata == {
            "name": "Activity Test Project",
        }
        assert activity.created_at is not None

    finally:
        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)

        if user is not None:
            db.delete(user)

        db.commit()
        db.close()


def test_create_project_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    captured = {}

    try:
        user = User(
            username=f"rollback_project_{unique_value}",
            email=f"rollback_project_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Rollback Test Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        def fail_record_activity(db, activity_data):
            # This function is reached only after create_project()
            # has already flushed the Project INSERT.
            captured["project_id"] = activity_data.project_id

            raise RuntimeError("Simulated activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        project_data = ProjectCreate(
            owner_id=user.id,
            name="Rollback Test Project",
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated activity failure",
        ):
            create_project(db, project_data)

        # The Project INSERT happened during flush(), but commit()
        # was never reached. Roll back the open transaction.
        db.rollback()

        project_id = captured["project_id"]

        # The Project must NOT exist after the rollback.
        assert db.get(Project, project_id) is None

        # The Activity must also NOT exist.
        activities = get_activities_for_project(
            db,
            project_id,
        )

        assert activities == []

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_soft_delete_project_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None

    try:
        user = User(
            username=f"projectdeleteaudit_{unique_value}",
            email=f"projectdeleteaudit_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Project Delete Audit User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Project Delete Audit Test",
            ),
        )

        deleted_project = soft_delete_project(
            db,
            project,
            user.id,
        )

        assert deleted_project.deleted_at is not None

        activities = get_activities_for_project(
            db,
            project.id,
        )

        delete_activities = [
            activity
            for activity in activities
            if activity.action == "PROJECT_DELETED"
        ]

        assert len(delete_activities) == 1

        activity = delete_activities[0]

        assert activity.project_id == project.id
        assert activity.task_id is None
        assert activity.actor_id == user.id
        assert activity.action == "PROJECT_DELETED"
        assert activity.activity_metadata == {
            "name": project.name,
        }
        assert activity.created_at is not None

    finally:
        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        if user is not None:
            db.delete(user)
            db.commit()

        db.close()
