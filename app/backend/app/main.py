from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.db.session import engine


app = FastAPI(
    title="DevOpsHub API",
    version="0.1.0",
)


app.include_router(users_router)
app.include_router(projects_router)

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
