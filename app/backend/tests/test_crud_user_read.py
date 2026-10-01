import uuid

from app.crud.user import create_user, get_user_by_id, get_users
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def test_get_user_by_id():
    unique_value = uuid.uuid4().hex[:8]

    user_data = UserCreate(
        username=f"readuser_{unique_value}",
        email=f"{unique_value}@example.com",
        password="strongpassword",
        name="Read User",
    )

    db = SessionLocal()
    user = None

    try:
        user = create_user(db, user_data)

        found_user = get_user_by_id(db, user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == user.username

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()


def test_get_users():
    unique_value = uuid.uuid4().hex[:8]

    user_data = UserCreate(
        username=f"listuser_{unique_value}",
        email=f"{unique_value}@example.com",
        password="strongpassword",
        name="List User",
    )

    db = SessionLocal()
    user = None

    try:
        user = create_user(db, user_data)

        users = get_users(db)

        assert any(existing.id == user.id for existing in users)

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()

