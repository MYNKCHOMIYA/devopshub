from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID

from app.crud.user import create_user,get_user_by_id,get_users,soft_delete_user
from app.schemas.user import UserCreate, UserResponse
from app.db.session import engine,get_db


app = FastAPI(
    title="DevOpsHub API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "devopshub-api",
    }


@app.get("/ready")
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "service": "devopshub-api",
                "database": "unavailable",
            },
        )

    return {
        "status": "ready",
        "service": "devopshub-api",
        "database": "ok",
    }



@app.post(
    "/users",
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


@app.get(
    "/users/{user_id}",
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


@app.get(
    "/users",
    response_model=list[UserResponse],
)
def get_users_endpoint(
    db: Session = Depends(get_db),
):
    return get_users(db)


@app.delete(
    "/users/{user_id}",
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
