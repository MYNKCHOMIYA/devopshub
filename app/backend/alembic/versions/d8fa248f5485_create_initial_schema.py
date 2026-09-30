"""create initial schema

Revision ID: d8fa248f5485
Revises:
Create Date: 2026-09-30 18:49:50.711272

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d8fa248f5485"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial DevOpsHub database schema."""

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_username"),
        "users",
        ["username"],
        unique=True,
    )

    # Projects
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('TODO', 'IN_PROGRESS', 'DONE')",
            name="ck_projects_status",
        ),
        sa.CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH')",
            name="ck_projects_priority",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_projects_owner_id"),
        "projects",
        ["owner_id"],
        unique=False,
    )

    # Tasks
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("assignee_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('TODO', 'IN_PROGRESS', 'DONE')",
            name="ck_tasks_status",
        ),
        sa.CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH')",
            name="ck_tasks_priority",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["assignee_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_tasks_project_id"),
        "tasks",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_tasks_created_by_id"),
        "tasks",
        ["created_by_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_tasks_assignee_id"),
        "tasks",
        ["assignee_id"],
        unique=False,
    )

    # Activities
    op.create_table(
        "activities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_activities_project_id"),
        "activities",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_task_id"),
        "activities",
        ["task_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_activities_actor_id"),
        "activities",
        ["actor_id"],
        unique=False,
    )

    # Comments
    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_comments_task_id"),
        "comments",
        ["task_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_comments_author_id"),
        "comments",
        ["author_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the DevOpsHub database schema."""

    # Comments
    op.drop_index(
        op.f("ix_comments_author_id"),
        table_name="comments",
    )

    op.drop_index(
        op.f("ix_comments_task_id"),
        table_name="comments",
    )

    op.drop_table("comments")

    # Activities
    op.drop_index(
        op.f("ix_activities_actor_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_task_id"),
        table_name="activities",
    )

    op.drop_index(
        op.f("ix_activities_project_id"),
        table_name="activities",
    )

    op.drop_table("activities")

    # Tasks
    op.drop_index(
        op.f("ix_tasks_assignee_id"),
        table_name="tasks",
    )

    op.drop_index(
        op.f("ix_tasks_created_by_id"),
        table_name="tasks",
    )

    op.drop_index(
        op.f("ix_tasks_project_id"),
        table_name="tasks",
    )

    op.drop_table("tasks")

    # Projects
    op.drop_index(
        op.f("ix_projects_owner_id"),
        table_name="projects",
    )

    op.drop_table("projects")

    # Users
    op.drop_index(
        op.f("ix_users_username"),
        table_name="users",
    )

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )

    op.drop_table("users")
