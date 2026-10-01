import uuid
from datetime import date

import pytest
from pydantic import ValidationError

from app.models.project import ProjectPriority, ProjectStatus
from app.schemas.project import ProjectCreate


def test_valid_project_create():
    owner_id = uuid.uuid4()

    project = ProjectCreate(
        owner_id=owner_id,
        name="DevOpsHub",
        description="Production-grade task management platform",
        status=ProjectStatus.TODO,
        priority=ProjectPriority.HIGH,
        start_date=date(2026, 10, 1),
        due_date=date(2026, 12, 31),
    )

    assert project.owner_id == owner_id
    assert project.name == "DevOpsHub"
    assert project.status == ProjectStatus.TODO
    assert project.priority == ProjectPriority.HIGH


def test_project_defaults():
    project = ProjectCreate(
        owner_id=uuid.uuid4(),
        name="Default Project",
    )

    assert project.status == ProjectStatus.TODO
    assert project.priority == ProjectPriority.MEDIUM
    assert project.description is None
    assert project.start_date is None
    assert project.due_date is None


def test_project_name_too_long():
    with pytest.raises(ValidationError):
        ProjectCreate(
            owner_id=uuid.uuid4(),
            name="x" * 151,
        )


def test_invalid_project_status():
    with pytest.raises(ValidationError):
        ProjectCreate(
            owner_id=uuid.uuid4(),
            name="Invalid Status Project",
            status="INVALID",
        )


def test_invalid_project_priority():
    with pytest.raises(ValidationError):
        ProjectCreate(
            owner_id=uuid.uuid4(),
            name="Invalid Priority Project",
            priority="INVALID",
        )
