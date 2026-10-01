from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

from datetime import datetime, timezone

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise

    return user


def get_users(db: Session) -> list[User]:
    statement = select(User).where(User.deleted_at.is_(None))
    result = db.execute(statement)

    return list(result.scalars().all())


def get_user_by_id(db: Session, user_id) -> User | None:
    statement = select(User).where(
        User.id == user_id,
        User.deleted_at.is_(None),
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def soft_delete_user(db: Session, user: User) -> User:
    user.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return user
