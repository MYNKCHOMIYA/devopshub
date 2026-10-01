import uuid

from app.crud.user import create_user
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def test_create_user():
    unique_value = uuid.uuid4().hex[:8]

    user_data = UserCreate(
        username=f"testuser_{unique_value}",
        email=f"{unique_value}@example.com",
        password="strongpassword",
        name="Test User",
    )

    db = SessionLocal()

    try:
        user = create_user(db, user_data)

        assert user.id is not None
        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.name == user_data.name
        assert user.password_hash != user_data.password
    finally:
        db.delete(user)
        db.commit()
        db.close()
