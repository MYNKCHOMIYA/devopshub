import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.models.activity import Activity

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.project import Project
from app.models.user import User



client = TestClient(app)


def test_create_project_api():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project_id = None

    try:
        user = User(
            username=f"api_project_{unique_value}",
            email=f"api_project_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="API Project Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        response = client.post(
            "/projects",
            json={
                "owner_id": str(user.id),
                "name": "API Test Project",
                "description": "Created by API test",
                "priority": "HIGH",
            },
        )

        assert response.status_code == 201

        data = response.json()
        project_id = data["id"]

        assert data["owner_id"] == str(user.id)
        assert data["name"] == "API Test Project"
        assert data["description"] == "Created by API test"
        assert data["status"] == "DONE"
        assert data["priority"] == "HIGH"
        assert "password_hash" not in data

    finally:
        if project_id is not None:
            project = db.get(Project, uuid.UUID(project_id))

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



def test_get_project_api():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project_id = None

    try:
        user = User(
            username=f"api_get_project_{unique_value}",
            email=f"api_get_project_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="API Get Project Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        create_response = client.post(
            "/projects",
            json={
                "owner_id": str(user.id),
                "name": "API GET Test Project",
                "description": "Project for GET endpoint test",
                "priority": "MEDIUM",
            },
        )

        assert create_response.status_code == 201

        created_data = create_response.json()
        project_id = created_data["id"]

        response = client.get(f"/projects/{project_id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == project_id
        assert data["owner_id"] == str(user.id)
        assert data["name"] == "API GET Test Project"
        assert data["description"] == "Project for GET endpoint test"
        assert data["status"] == "TODO"
        assert data["priority"] == "MEDIUM"

    finally:
        if project_id is not None:
            project = db.get(Project, uuid.UUID(project_id))

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


def test_get_project_api_not_found():
    project_id = uuid.uuid4()

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found.",
    }


def test_get_projects_api():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project_ids = []

    try:
        user = User(
            username=f"api_list_{unique_value}",
            email=f"api_list_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="API List Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        for project_name in ["API Project One", "API Project Two"]:
            response = client.post(
                "/projects",
                json={
                    "owner_id": str(user.id),
                    "name": project_name,
                },
            )

            assert response.status_code == 201
            project_ids.append(response.json()["id"])

        response = client.get("/projects")

        assert response.status_code == 200

        data = response.json()

        returned_ids = {project["id"] for project in data}

        assert project_ids[0] in returned_ids
        assert project_ids[1] in returned_ids

    finally:
        for project_id in project_ids:
            project = db.get(Project, uuid.UUID(project_id))

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


def test_delete_project_api():
    unique_value = uuid.uuid4().hex[:8]

    db = SessionLocal()
    user = None
    project_id = None

    try:
        user = User(
            username=f"api_delete_{unique_value}",
            email=f"api_delete_{unique_value}@example.com",
            password_hash=hash_password("strongpassword"),
            name="API Delete Owner",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        create_response = client.post(
            "/projects",
            json={
                "owner_id": str(user.id),
                "name": "API Delete Test Project",
            },
        )

        assert create_response.status_code == 201

        project_id = create_response.json()["id"]

        delete_response = client.delete(
            f"/projects/{project_id}"
        )

        assert delete_response.status_code == 204
        assert delete_response.content == b""
        deleted_project = db.get(Project, uuid.UUID(project_id))

        assert deleted_project is not None
        assert deleted_project.deleted_at is not None
        assert deleted_project.deleted_at.tzinfo is not None

        get_response = client.get(
            f"/projects/{project_id}"
        )

        assert get_response.status_code == 404
        assert get_response.json() == {
            "detail": "Project not found.",
        }

    finally:
        if project_id is not None:
            project = db.get(Project, uuid.UUID(project_id))

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
