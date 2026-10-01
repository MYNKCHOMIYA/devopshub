from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.user import (
    create_user,
    get_user_by_id,
    get_users,
    soft_delete_user,
)
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
)
def create_user_endpoint(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_user(db, user_data)

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists.",
        )


@router.get(
    "",
    response_model=list[UserResponse],
)
def get_users_endpoint(
    db: Session = Depends(get_db),
):
    return get_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=204,
)
def delete_user_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    soft_delete_user(db, user)

    return None
