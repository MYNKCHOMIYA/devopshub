import uuid

from app.crud.user import create_user, get_user_by_id, soft_delete_user
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def test_soft_delete_user():
    unique_value = uuid.uuid4().hex[:8]

    user_data = UserCreate(
        username=f"deleteuser_{unique_value}",
        email=f"{unique_value}@example.com",
        password="strongpassword",
        name="Delete User",
    )

    db = SessionLocal()
    user = None

    try:
        user = create_user(db, user_data)

        deleted_user = soft_delete_user(db, user)

        assert deleted_user.deleted_at is not None

        found_user = get_user_by_id(db, user.id)

        assert found_user is None

        db.refresh(user)

        assert user.deleted_at is not None

    finally:
        if user is not None:
            db.delete(user)
            db.commit()

        db.close()
