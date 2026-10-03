import uuid

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.project import Project
from app.models.user import User


client = TestClient(app)


def test_create_task_api():
    db = SessionLocal()

    user = User(
        username=f"taskapi_{uuid.uuid4().hex[:8]}",
        email=f"taskapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Task API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    project = Project(
        owner_id=user.id,
        name="Task API Project",
        description="Project for Task API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    user_id = user.id
    project_id =project.id

    db.close()

    response = client.post(
        "/tasks",
        json={
            "project_id": str(project_id),
            "created_by_id": str(user_id),
            "assignee_id": str(user.id),
            "title": "Build Task API",
            "description": "Create the first Task API endpoint test.",
            "status": "TODO",
            "priority": "MEDIUM",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == str(project_id)
    assert data["created_by_id"] == str(user_id)
    assert data["assignee_id"] == str(user.id)
    assert data["title"] == "Build Task API"
    assert data["description"] == "Create the first Task API endpoint test."
    assert data["status"] == "TODO"
    assert data["priority"] == "MEDIUM"


def test_get_task_api():
    db = SessionLocal()

    user = User(
        username=f"taskget_{uuid.uuid4().hex[:8]}",
        email=f"taskget_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Task GET User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Task GET Project",
        description="Project for Task GET testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    db.close()

    create_response = client.post(
        "/tasks",
        json={
            "project_id": str(project_id),
            "created_by_id": str(user_id),
            "assignee_id": str(user_id),
            "title": "Get Task API",
            "description": "Test retrieving a task.",
            "status": "TODO",
            "priority": "MEDIUM",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["project_id"] == str(project_id)
    assert data["created_by_id"] == str(user_id)
    assert data["assignee_id"] == str(user_id)
    assert data["title"] == "Get Task API"
    assert data["description"] == "Test retrieving a task."
    assert data["status"] == "TODO"
    assert data["priority"] == "MEDIUM"



def test_get_tasks_api():
    db = SessionLocal()

    user = User(
        username=f"tasklist_{uuid.uuid4().hex[:8]}",
        email=f"tasklist_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Task List User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Task List Project",
        description="Project for Task list testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    db.close()

    response_1 = client.post(
        "/tasks",
        json={
            "project_id": str(project_id),
            "created_by_id": str(user_id),
            "assignee_id": str(user_id),
            "title": "Task One",
            "description": "First task.",
            "status": "TODO",
            "priority": "LOW",
        },
    )

    response_2 = client.post(
        "/tasks",
        json={
            "project_id": str(project_id),
            "created_by_id": str(user_id),
            "assignee_id": str(user_id),
            "title": "Task Two",
            "description": "Second task.",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
        },
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    task_1_id = response_1.json()["id"]
    task_2_id = response_2.json()["id"]

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    returned_ids = {task["id"] for task in data}

    assert task_1_id in returned_ids
    assert task_2_id in returned_ids



def test_get_task_api_not_found():
    task_id = uuid.uuid4()

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found.",
    }


def test_delete_task_api():
    db = SessionLocal()

    user = User(
        username=f"taskdelete_{uuid.uuid4().hex[:8]}",
        email=f"taskdelete_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Task Delete User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Task Delete Project",
        description="Project for Task DELETE testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    project_id = project.id

    db.close()

    create_response = client.post(
        "/tasks",
        json={
            "project_id": str(project_id),
            "created_by_id": str(user_id),
            "assignee_id": str(user_id),
            "title": "Delete Task API",
            "description": "Test soft deleting a task.",
            "status": "TODO",
            "priority": "MEDIUM",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    db = SessionLocal()

    from uuid import UUID

    from app.models.task import Task

    deleted_task = db.get(Task, UUID(task_id))

    assert deleted_task is not None
    assert deleted_task.deleted_at is not None
    assert deleted_task.deleted_at.tzinfo is not None

    db.close()

    get_response = client.get(f"/tasks/{task_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Task not found.",
    }
