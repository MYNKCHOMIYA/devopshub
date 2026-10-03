import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.core.security import hash_password
from app.crud.task import (
    create_task,
    get_task_by_id,
    get_tasks,
    soft_delete_task,
)
from app.crud.project import create_project
from app.db.session import SessionLocal
from app.models.task import TaskPriority, TaskStatus
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
            db.delete(task)
            db.commit()

        if project is not None:
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
            db.delete(task)
            db.commit()

        if project is not None:
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
            db.delete(task_one)
            db.commit()

        if task_two is not None:
            db.delete(task_two)
            db.commit()

        if project is not None:
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
            db.delete(active_task)
            db.commit()

        if deleted_task is not None:
            db.delete(deleted_task)
            db.commit()

        if project is not None:
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

        deleted_task = soft_delete_task(db, task)

        assert deleted_task.deleted_at is not None
        assert isinstance(deleted_task.deleted_at, datetime)
        assert deleted_task.deleted_at.tzinfo is not None

    finally:
        if task is not None:
            db.delete(task)
            db.commit()

        if project is not None:
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
