import uuid

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


client = TestClient(app)


def test_create_comment_api():
    db = SessionLocal()

    user = User(
        username=f"commentapi_{uuid.uuid4().hex[:8]}",
        email=f"commentapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment API Project",
        description="Project for Comment API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment API Task",
        description="Task for Comment API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.post(
        "/comments",
        json={
            "task_id": str(task_id),
            "author_id": str(user_id),
            "content": "This comment was created through the API.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["task_id"] == str(task_id)
    assert data["author_id"] == str(user_id)
    assert data["content"] == "This comment was created through the API."
    assert data["id"] is not None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_get_comment_api():
    db = SessionLocal()

    user = User(
        username=f"commentgetapi_{uuid.uuid4().hex[:8]}",
        email=f"commentgetapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment GET API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment GET API Project",
        description="Project for Comment GET API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment GET API Task",
        description="Task for Comment GET API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    create_response = client.post(
        "/comments",
        json={
            "task_id": str(task_id),
            "author_id": str(user_id),
            "content": "Retrieve this comment.",
        },
    )

    assert create_response.status_code == 201

    comment_id = create_response.json()["id"]

    response = client.get(f"/comments/{comment_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == comment_id
    assert data["task_id"] == str(task_id)
    assert data["author_id"] == str(user_id)
    assert data["content"] == "Retrieve this comment."


def test_get_task_comments_api():
    db = SessionLocal()

    user = User(
        username=f"commentlistapi_{uuid.uuid4().hex[:8]}",
        email=f"commentlistapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment List API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment List API Project",
        description="Project for Comment list API testing.",
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
        title="Comment List API Task One",
        description="First task.",
        status="TODO",
        priority="MEDIUM",
    )

    task_2 = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment List API Task Two",
        description="Second task.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add_all([task_1, task_2])
    db.commit()
    db.refresh(task_1)
    db.refresh(task_2)

    task_1_id = task_1.id
    task_2_id = task_2.id

    db.close()

    response_1 = client.post(
        "/comments",
        json={
            "task_id": str(task_1_id),
            "author_id": str(user_id),
            "content": "First task comment.",
        },
    )

    response_2 = client.post(
        "/comments",
        json={
            "task_id": str(task_1_id),
            "author_id": str(user_id),
            "content": "Second task comment.",
        },
    )

    response_3 = client.post(
        "/comments",
        json={
            "task_id": str(task_2_id),
            "author_id": str(user_id),
            "content": "Other task comment.",
        },
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 201
    assert response_3.status_code == 201

    comment_1_id = response_1.json()["id"]
    comment_2_id = response_2.json()["id"]
    comment_3_id = response_3.json()["id"]

    response = client.get(f"/comments/task/{task_1_id}")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    returned_ids = {comment["id"] for comment in data}

    assert comment_1_id in returned_ids
    assert comment_2_id in returned_ids
    assert comment_3_id not in returned_ids


def test_get_comment_api_not_found():
    comment_id = uuid.uuid4()

    response = client.get(f"/comments/{comment_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Comment not found.",
    }


def test_delete_comment_api():
    db = SessionLocal()

    user = User(
        username=f"commentdeleteapi_{uuid.uuid4().hex[:8]}",
        email=f"commentdeleteapi_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("testpassword"),
        name="Comment Delete API User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = user.id

    project = Project(
        owner_id=user_id,
        name="Comment Delete API Project",
        description="Project for Comment DELETE API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    task = Task(
        project_id=project.id,
        created_by_id=user_id,
        assignee_id=user_id,
        title="Comment Delete API Task",
        description="Task for Comment DELETE API testing.",
        status="TODO",
        priority="MEDIUM",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    create_response = client.post(
        "/comments",
        json={
            "task_id": str(task_id),
            "author_id": str(user_id),
            "content": "This comment will be deleted.",
        },
    )

    assert create_response.status_code == 201

    comment_id = create_response.json()["id"]

    delete_response = client.delete(f"/comments/{comment_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/comments/{comment_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Comment not found.",
    }
