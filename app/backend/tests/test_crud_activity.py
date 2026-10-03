import uuid

from app.core.security import hash_password
from app.crud.activity import (
    create_activity,
    get_activities_for_project,
    get_activities_for_task,
    get_activity_by_id,
)
from app.db.session import SessionLocal
from app.models.activity import Activity
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.activity import ActivityCreate


def test_create_activity():
    db = SessionLocal()

    user = User(
        username=f"activity_{uuid.uuid4().hex[:8]}",
        email=f"activity_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity Project",
        description="Project for activity CRUD testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    activity_data = ActivityCreate(
        project_id=project_id,
        actor_id=user_id,
        action="PROJECT_CREATED",
        metadata={
            "name": project.name,
        },
    )

    activity = create_activity(db, activity_data)

    assert activity.id is not None
    assert activity.project_id == project_id
    assert activity.task_id is None
    assert activity.actor_id == user_id
    assert activity.action == "PROJECT_CREATED"
    assert activity.activity_metadata == {
        "name": "Activity Project",
    }
    assert activity.created_at is not None

    db.close()


def test_get_activity_by_id():
    db = SessionLocal()

    user = User(
        username=f"activityget_{uuid.uuid4().hex[:8]}",
        email=f"activityget_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity Get User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity Get Project",
        description="Project for activity get testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    activity = create_activity(
        db,
        ActivityCreate(
            project_id=project.id,
            actor_id=user_id,
            action="PROJECT_CREATED",
            metadata={},
        ),
    )

    found_activity = get_activity_by_id(
        db,
        activity.id,
    )

    assert found_activity is not None
    assert found_activity.id == activity.id
    assert found_activity.project_id == project.id
    assert found_activity.actor_id == user_id
    assert found_activity.action == "PROJECT_CREATED"

    db.close()


def test_get_activities_for_project():
    db = SessionLocal()

    user = User(
        username=f"activitylist_{uuid.uuid4().hex[:8]}",
        email=f"activitylist_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity List User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project_1 = Project(
        owner_id=user_id,
        name="Activity List Project One",
        description="First project.",
        status="TODO",
        priority="MEDIUM",
    )

    project_2 = Project(
        owner_id=user_id,
        name="Activity List Project Two",
        description="Second project.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add_all([project_1, project_2])
    db.commit()
    db.refresh(project_1)
    db.refresh(project_2)

    activity_1 = create_activity(
        db,
        ActivityCreate(
            project_id=project_1.id,
            actor_id=user_id,
            action="PROJECT_CREATED",
            metadata={
                "project": "one",
            },
        ),
    )

    activity_2 = create_activity(
        db,
        ActivityCreate(
            project_id=project_1.id,
            actor_id=user_id,
            action="TASK_CREATED",
            metadata={
                "task": "one",
            },
        ),
    )

    activity_3 = create_activity(
        db,
        ActivityCreate(
            project_id=project_2.id,
            actor_id=user_id,
            action="PROJECT_CREATED",
            metadata={
                "project": "two",
            },
        ),
    )

    activities = get_activities_for_project(
        db,
        project_1.id,
    )

    assert len(activities) == 2

    activity_ids = {
        activity.id
        for activity in activities
    }

    assert activity_1.id in activity_ids
    assert activity_2.id in activity_ids
    assert activity_3.id not in activity_ids

    db.close()


def test_get_activities_for_task():
    db = SessionLocal()

    user = User(
        username=f"activitytask_{uuid.uuid4().hex[:8]}",
        email=f"activitytask_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity Task User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity Task Project",
        description="Project for activity task testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task_1 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Activity Task One",
        description="First task.",
        status="TODO",
        priority="MEDIUM",
    )

    task_2 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Activity Task Two",
        description="Second task.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add_all([task_1, task_2])
    db.commit()
    db.refresh(task_1)
    db.refresh(task_2)

    activity_1 = create_activity(
        db,
        ActivityCreate(
            project_id=project.id,
            task_id=task_1.id,
            actor_id=user_id,
            action="TASK_CREATED",
            metadata={
                "title": task_1.title,
            },
        ),
    )

    activity_2 = create_activity(
        db,
        ActivityCreate(
            project_id=project.id,
            task_id=task_2.id,
            actor_id=user_id,
            action="TASK_CREATED",
            metadata={
                "title": task_2.title,
            },
        ),
    )

    activities = get_activities_for_task(
        db,
        task_1.id,
    )

    assert len(activities) == 1
    assert activities[0].id == activity_1.id
    assert activities[0].task_id == task_1.id
    assert activity_2.id not in {
        activity.id
        for activity in activities
    }

    db.close()


def test_get_activity_not_found():
    db = SessionLocal()

    result = get_activity_by_id(
        db,
        uuid.uuid4(),
    )

    assert result is None

    db.close()
