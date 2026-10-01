from app.core.security import hash_password, verify_password


def test_password_hashing():
    password = "strongpassword"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrongpassword", password_hash) is False


def test_same_password_generates_different_hashes():
    password = "strongpassword"

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two
    assert verify_password(password, hash_one) is True
    assert verify_password(password, hash_two) is True

