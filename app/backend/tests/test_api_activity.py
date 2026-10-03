import uuid

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.crud.activity import create_activity
from app.db.session import SessionLocal
from app.main import app
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.activity import ActivityCreate


client = TestClient(app)


def test_create_activity_api():
    db = SessionLocal()

    user = User(
        username=f"activityapi_{uuid.uuid4().hex[:8]}",
        email=f"activityapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity API Project",
        description="Project for Activity API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    db.close()

    response = client.post(
        "/activities",
        json={
            "project_id": str(project_id),
            "actor_id": str(user_id),
            "action": "PROJECT_CREATED",
            "metadata": {
                "name": "Activity API Project",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["project_id"] == str(project_id)
    assert data["task_id"] is None
    assert data["actor_id"] == str(user_id)
    assert data["action"] == "PROJECT_CREATED"
    assert data["metadata"] == {
        "name": "Activity API Project",
    }
    assert data["created_at"] is not None


def test_get_activity_api():
    db = SessionLocal()

    user = User(
        username=f"activityapiget_{uuid.uuid4().hex[:8]}",
        email=f"activityapiget_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity API Get User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity API Get Project",
        description="Project for Activity API get testing.",
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
            metadata={
                "name": project.name,
            },
        ),
    )

    activity_id = activity.id
    project_id = project.id

    db.close()

    response = client.get(
        f"/activities/{activity_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(activity_id)
    assert data["project_id"] == str(project_id)
    assert data["actor_id"] == str(user_id)
    assert data["action"] == "PROJECT_CREATED"
    assert data["metadata"] == {
        "name": "Activity API Get Project",
    }
    assert data["created_at"] is not None


def test_get_project_activities_api():
    db = SessionLocal()

    user = User(
        username=f"activityapiproject_{uuid.uuid4().hex[:8]}",
        email=f"activityapiproject_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity API Project User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project_1 = Project(
        owner_id=user_id,
        name="Activity API Project One",
        description="First project.",
        status="TODO",
        priority="MEDIUM",
    )

    project_2 = Project(
        owner_id=user_id,
        name="Activity API Project Two",
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

    activity_1_id = activity_1.id
    activity_2_id = activity_2.id
    activity_3_id = activity_3.id
    project_id = project_1.id

    db.close()

    response = client.get(
        f"/activities/project/{project_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    activity_ids = {
        activity["id"]
        for activity in data
    }

    assert str(activity_1_id) in activity_ids
    assert str(activity_2_id) in activity_ids
    assert str(activity_3_id) not in activity_ids


def test_get_task_activities_api():
    db = SessionLocal()

    user = User(
        username=f"activityapitask_{uuid.uuid4().hex[:8]}",
        email=f"activityapitask_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Activity API Task User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Activity API Task Project",
        description="Project for task Activity API testing.",
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
        title="Activity API Task One",
        description="First task.",
        status="TODO",
        priority="MEDIUM",
    )

    task_2 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Activity API Task Two",
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

    activity_1_id = activity_1.id
    activity_2_id = activity_2.id
    task_1_id = task_1.id

    db.close()

    response = client.get(
        f"/activities/task/{task_1_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(activity_1_id)
    assert data[0]["task_id"] == str(task_1_id)
    assert data[0]["id"] != str(activity_2_id)


def test_get_activity_api_not_found():
    response = client.get(
        f"/activities/{uuid.uuid4()}",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found."
