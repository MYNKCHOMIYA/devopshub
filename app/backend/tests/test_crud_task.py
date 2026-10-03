import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.crud.activity import get_activities_for_task
from app.crud.project import create_project
from app.crud.task import (
    create_task,
    get_task_by_id,
    get_tasks,
    soft_delete_task,
    update_task_status,
    update_task_assignee,
)
from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.project import ProjectCreate
from app.schemas.task import TaskCreate


def test_create_task():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"taskcreator_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Creator",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Test Project",
            ),
        )

        task_data = TaskCreate(
            project_id=project.id,
            created_by_id=user.id,
            assignee_id=user.id,
            title="Build Task CRUD",
            description="Implement production-style task CRUD.",
        )

        task = create_task(db, task_data)

        assert task.id is not None
        assert task.project_id == project.id
        assert task.created_by_id == user.id
        assert task.assignee_id == user.id
        assert task.title == "Build Task CRUD"
        assert task.description == "Implement production-style task CRUD."
        assert task.status == TaskStatus.TODO.value
        assert task.priority == TaskPriority.MEDIUM.value

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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


def test_get_task_by_id():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"taskreader_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Reader",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Read Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Read Task",
            ),
        )

        found_task = get_task_by_id(db, task.id)

        assert found_task is not None
        assert found_task.id == task.id
        assert found_task.project_id == project.id
        assert found_task.title == "Read Task"

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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


def test_get_tasks():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task_one = None
    task_two = None

    try:
        user = User(
            username=f"tasklist_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task List User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task List Project",
            ),
        )

        task_one = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Task One",
            ),
        )

        task_two = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Task Two",
            ),
        )

        tasks = get_tasks(db)

        task_ids = {task.id for task in tasks}

        assert task_one.id in task_ids
        assert task_two.id in task_ids

    finally:
        if task_one is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task_one.id
                )
            )
            db.delete(task_one)
            db.commit()

        if task_two is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task_two.id
                )
            )
            db.delete(task_two)
            db.commit()

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


def test_get_tasks_excludes_deleted_tasks():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    active_task = None
    deleted_task = None

    try:
        user = User(
            username=f"tasksoftdelete_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Soft Delete User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Soft Delete Project",
            ),
        )

        active_task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Active Task",
            ),
        )

        deleted_task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Deleted Task",
            ),
        )

        deleted_task.deleted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(deleted_task)

        tasks = get_tasks(db)

        task_ids = {task.id for task in tasks}

        assert active_task.id in task_ids
        assert deleted_task.id not in task_ids

    finally:
        if active_task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == active_task.id
                )
            )
            db.delete(active_task)
            db.commit()

        if deleted_task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == deleted_task.id
                )
            )
            db.delete(deleted_task)
            db.commit()

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


def test_soft_delete_task():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"taskdelete_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Delete User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Delete Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Task To Delete",
            ),
        )

        deleted_task = soft_delete_task(db, task,user.id)

        assert deleted_task.deleted_at is not None
        assert isinstance(deleted_task.deleted_at, datetime)
        assert deleted_task.deleted_at.tzinfo is not None

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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




def test_create_task_with_nonexistent_project():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None

    try:
        user = User(
            username=f"taskinvalidproject_{unique_value}",
            email=f"{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Invalid Project User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        task_data = TaskCreate(
            project_id=uuid.uuid4(),
            created_by_id=user.id,
            assignee_id=user.id,
            title="Invalid Project Task",
        )

        with pytest.raises(IntegrityError):
            create_task(db, task_data)

        db.rollback()

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_create_task_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"task_activity_{unique_value}",
            email=f"task_activity_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Activity Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Activity Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Audit Test Task",
                description="Verify TASK_CREATED activity.",
            ),
        )

        activities = get_activities_for_task(
            db,
            task.id,
        )

        assert len(activities) == 1

        activity = activities[0]

        assert activity.project_id == project.id
        assert activity.task_id == task.id
        assert activity.actor_id == user.id
        assert activity.action == "TASK_CREATED"
        assert activity.activity_metadata == {
            "title": "Audit Test Task",
        }
        assert activity.created_at is not None

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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


def test_create_task_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    captured = {}

    try:
        user = User(
            username=f"task_rollback_{unique_value}",
            email=f"task_rollback_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Rollback Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Rollback Project",
            ),
        )

        def fail_record_activity(db, activity_data):
            # create_task() has already called flush(),
            # so the Task ID exists inside the current transaction.
            captured["task_id"] = activity_data.task_id

            raise RuntimeError("Simulated task activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        task_data = TaskCreate(
            project_id=project.id,
            created_by_id=user.id,
            assignee_id=user.id,
            title="Rollback Test Task",
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated task activity failure",
        ):
            create_task(db, task_data)

        # The Task was flushed but never committed.
        # Roll back the transaction.
        db.rollback()

        task_id = captured["task_id"]

        # The Task must not exist after rollback.
        assert db.get(Task, task_id) is None

        # No TASK_CREATED Activity can remain for that Task.
        activities = get_activities_for_task(
            db,
            task_id,
        )

        assert activities == []

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


def test_update_task_status_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"status_{unique_value}",
            email=f"status_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Status Test User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Status Change Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Status Change Task",
            ),
        )

        assert task.status == TaskStatus.TODO.value

        updated_task = update_task_status(
            db,
            task,
            TaskStatus.IN_PROGRESS,
            user.id,
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS.value

        activities = get_activities_for_task(
            db,
            task.id,
        )

        status_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_STATUS_CHANGED"
        ]

        assert len(status_activities) == 1

        activity = status_activities[0]

        assert activity.project_id == project.id
        assert activity.task_id == task.id
        assert activity.actor_id == user.id
        assert activity.action == "TASK_STATUS_CHANGED"
        assert activity.activity_metadata == {
            "old_status": "TODO",
            "new_status": "IN_PROGRESS",
        }
        assert activity.created_at is not None

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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



def test_update_task_status_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"statusrollback_{unique_value}",
            email=f"statusrollback_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Status Rollback User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Status Rollback Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Status Rollback Task",
            ),
        )

        assert task.status == TaskStatus.TODO.value

        def fail_record_activity(db, activity_data):
            raise RuntimeError("Simulated status activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated status activity failure",
        ):
            update_task_status(
                db,
                task,
                TaskStatus.IN_PROGRESS,
                user.id,
            )

        # The status update was flushed but never committed.
        db.rollback()

        # Re-read the task from the database.
        refreshed_task = get_task_by_id(
            db,
            task.id,
        )

        assert refreshed_task is not None
        assert refreshed_task.status == TaskStatus.TODO.value

        # TASK_STATUS_CHANGED must not exist.
        activities = get_activities_for_task(
            db,
            task.id,
        )

        status_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_STATUS_CHANGED"
        ]

        assert status_activities == []

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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


def test_update_task_assignee_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    actor = None
    old_assignee = None
    new_assignee = None
    project = None
    task = None

    try:
        actor = User(
            username=f"assignactor_{unique_value}",
            email=f"assignactor_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Assignment Actor",
        )

        old_assignee = User(
            username=f"assignold_{unique_value}",
            email=f"assignold_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Old Assignee",
        )

        new_assignee = User(
            username=f"assignnew_{unique_value}",
            email=f"assignnew_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="New Assignee",
        )

        db.add_all([actor, old_assignee, new_assignee])
        db.commit()

        db.refresh(actor)
        db.refresh(old_assignee)
        db.refresh(new_assignee)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=actor.id,
                name="Task Assignment Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=actor.id,
                assignee_id=old_assignee.id,
                title="Assignment Test Task",
            ),
        )

        assert task.assignee_id == old_assignee.id

        updated_task = update_task_assignee(
            db,
            task,
            new_assignee.id,
            actor.id,
        )

        assert updated_task.assignee_id == new_assignee.id

        activities = get_activities_for_task(
            db,
            task.id,
        )

        assignment_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_ASSIGNED"
        ]

        assert len(assignment_activities) == 1

        activity = assignment_activities[0]

        assert activity.project_id == project.id
        assert activity.task_id == task.id
        assert activity.actor_id == actor.id
        assert activity.action == "TASK_ASSIGNED"
        assert activity.activity_metadata == {
            "old_assignee_id": str(old_assignee.id),
            "new_assignee_id": str(new_assignee.id),
        }
        assert activity.created_at is not None

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        for user in [actor, old_assignee, new_assignee]:
            if user is not None:
                db.delete(user)
                db.commit()

        db.close()


def test_update_task_assignee_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    actor = None
    old_assignee = None
    new_assignee = None
    project = None
    task = None

    try:
        actor = User(
            username=f"assignrollbackactor_{unique_value}",
            email=f"assignrollbackactor_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Assignment Rollback Actor",
        )

        old_assignee = User(
            username=f"assignrollbackold_{unique_value}",
            email=f"assignrollbackold_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Old Rollback Assignee",
        )

        new_assignee = User(
            username=f"assignrollbacknew_{unique_value}",
            email=f"assignrollbacknew_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="New Rollback Assignee",
        )

        db.add_all([
            actor,
            old_assignee,
            new_assignee,
        ])
        db.commit()

        db.refresh(actor)
        db.refresh(old_assignee)
        db.refresh(new_assignee)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=actor.id,
                name="Assignment Rollback Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=actor.id,
                assignee_id=old_assignee.id,
                title="Assignment Rollback Task",
            ),
        )

        assert task.assignee_id == old_assignee.id

        def fail_record_activity(db, activity_data):
            raise RuntimeError("Simulated assignment activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated assignment activity failure",
        ):
            update_task_assignee(
                db,
                task,
                new_assignee.id,
                actor.id,
            )

        # The assignment update was flushed but never committed.
        db.rollback()

        # Re-read from the database to verify the rollback.
        refreshed_task = get_task_by_id(
            db,
            task.id,
        )

        assert refreshed_task is not None
        assert refreshed_task.assignee_id == old_assignee.id

        # TASK_ASSIGNED must not exist.
        activities = get_activities_for_task(
            db,
            task.id,
        )

        assignment_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_ASSIGNED"
        ]

        assert assignment_activities == []

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

        if project is not None:
            db.execute(
                delete(Activity).where(
                    Activity.project_id == project.id
                )
            )
            db.delete(project)
            db.commit()

        for user in [actor, old_assignee, new_assignee]:
            if user is not None:
                db.delete(user)
                db.commit()

        db.close()


def test_soft_delete_task_records_activity():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"taskdeleteaudit_{unique_value}",
            email=f"taskdeleteaudit_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Task Delete Audit User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Task Delete Audit Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Task Delete Audit Test",
            ),
        )

        deleted_task = soft_delete_task(
            db,
            task,
            user.id,
        )

        assert deleted_task.deleted_at is not None
        assert deleted_task.deleted_at.tzinfo is not None

        activities = get_activities_for_task(
            db,
            task.id,
        )

        delete_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_DELETED"
        ]

        assert len(delete_activities) == 1

        activity = delete_activities[0]

        assert activity.project_id == project.id
        assert activity.task_id == task.id
        assert activity.actor_id == user.id
        assert activity.action == "TASK_DELETED"
        assert activity.activity_metadata == {
            "title": task.title,
        }
        assert activity.created_at is not None

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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




def test_soft_delete_task_rolls_back_when_activity_fails(monkeypatch):
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project = None
    task = None

    try:
        user = User(
            username=f"deleterollback_{unique_value}",
            email=f"deleterollback_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="Delete Rollback User",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        project = create_project(
            db,
            ProjectCreate(
                owner_id=user.id,
                name="Delete Rollback Project",
            ),
        )

        task = create_task(
            db,
            TaskCreate(
                project_id=project.id,
                created_by_id=user.id,
                assignee_id=user.id,
                title="Delete Rollback Task",
            ),
        )

        assert task.deleted_at is None

        def fail_record_activity(db, activity_data):
            raise RuntimeError("Simulated delete activity failure")

        monkeypatch.setattr(
            "app.crud.activity.record_activity",
            fail_record_activity,
        )

        with pytest.raises(
            RuntimeError,
            match="Simulated delete activity failure",
        ):
            soft_delete_task(
                db,
                task,
                user.id,
            )

        # The soft delete was flushed but never committed.
        db.rollback()

        # Re-read the task from the database.
        refreshed_task = db.get(
            Task,
            task.id,
        )

        assert refreshed_task is not None
        assert refreshed_task.deleted_at is None

        # TASK_DELETED must not exist.
        activities = get_activities_for_task(
            db,
            task.id,
        )

        delete_activities = [
            activity
            for activity in activities
            if activity.action == "TASK_DELETED"
        ]

        assert delete_activities == []

    finally:
        if task is not None:
            db.execute(
                delete(Activity).where(
                    Activity.task_id == task.id
                )
            )
            db.delete(task)
            db.commit()

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
