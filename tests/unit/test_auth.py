import bcrypt
import pytest

from app.core.security import get_password_hash, verify_password


@pytest.mark.unit
def test_get_password_hash():
    password = "my_secret_password"
    hashed_password = get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    bcrypt.checkpw(password.encode(), hashed_password.encode())


@pytest.mark.unit
def test_verify_password():
    # Test Case 1: Correct password
    plain_password = "my_secret_password"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True

    # Test Case 2: Incorrect password
    wrong_password = "wrong_password"
    assert verify_password(wrong_password, hashed_password) is False

    # Test Case 3: Empty password
    empty_password = ""
    assert verify_password(empty_password, hashed_password) is False
