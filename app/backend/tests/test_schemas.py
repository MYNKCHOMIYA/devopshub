import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_valid_user_create():
    user = UserCreate(
        username="mayank",
        email="mayank@example.com",
        password="strongpassword",
        name="Mayank",
    )

    assert user.username == "mayank"
    assert user.email == "mayank@example.com"
    assert user.phone is None


def test_username_too_short():
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="mayank@example.com",
            password="strongpassword",
            name="Mayank",
        )


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="mayank",
            email="not-an-email",
            password="strongpassword",
            name="Mayank",
        )


def test_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(
            username="mayank",
            email="mayank@example.com",
            password="short",
            name="Mayank",
        )


def test_optional_phone():
    user = UserCreate(
        username="mayank",
        email="mayank@example.com",
        password="strongpassword",
        name="Mayank",
        phone="+919876543210",
    )

    assert user.phone == "+919876543210"
