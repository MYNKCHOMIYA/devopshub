import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    task_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("tasks.id"),
        nullable=True,
        index=True,
    )

    actor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    activity_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
	server_default=func.now(),
    )
