from datetime import timedelta

import bcrypt
import pytest
from fastapi import HTTPException

import app.models as models
from app.database import TokenBlacklistORM
from app.routers.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user,
)


@pytest.mark.integration
def test_get_user(user_payload, db_session):
    # inject user in db
    hashed_password = get_password_hash(user_payload["password"])
    new_user = models.UserORM(
        username=user_payload["username"],
        email=user_payload["email"],
        hashed_password=hashed_password,
    )
    db_session.add(new_user)
    db_session.commit()

    # retrieve the user
    user = get_user(user_payload["username"], db_session)
    assert user
    assert user.username == user_payload["username"]
    assert user.email == user_payload["email"]

    # retrieve inexistent user
    user = get_user("inexistent_user", db_session)
    assert user is None


@pytest.mark.api
@pytest.mark.integration
def test_register(test_client, user_payload, register_endpoint, db_session):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data["status"] == "Success"
    assert (
        response_data["message"]
        == f"User {user_payload["username"]} registered successfully."
    )

    user = (
        db_session.query(models.UserORM)
        .filter_by(username=user_payload["username"])
        .first()
    )
    assert user is not None
    assert user.username == user_payload["username"]
    assert user.email == user_payload["email"]

    plaintext_password = user_payload["password"]
    assert bcrypt.checkpw(
        plaintext_password.encode(), user.hashed_password.encode()
    )


@pytest.mark.api
@pytest.mark.integration
def test_login(test_client, user_payload, register_endpoint, login_endpoint):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )
    response = test_client.post(
        login_endpoint,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user_payload["username"],
            "password": user_payload["password"],
        },
    )
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["token_type"] == "bearer"
    assert "access_token" in response_data
    assert response_data["access_token"] != ""


@pytest.mark.api
@pytest.mark.integration
def test_logout(
    test_client,
    user_payload,
    register_endpoint,
    login_endpoint,
    logout_endpoint,
    db_session,
):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )
    response = test_client.post(
        login_endpoint,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user_payload["username"],
            "password": user_payload["password"],
        },
    )
    access_token = response.json()["access_token"]
    response = test_client.post(
        logout_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["message"] == "Logged out successfully"

    blacklisted_token = (
        db_session.query(TokenBlacklistORM)
        .filter_by(token=access_token)
        .first()
    )
    assert blacklisted_token is not None


@pytest.mark.api
@pytest.mark.integration
def test_get_current_user(
    test_client,
    user_payload,
    register_endpoint,
    login_endpoint,
    logout_endpoint,
    db_session,
):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )
    response = test_client.post(
        login_endpoint,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": user_payload["username"],
            "password": user_payload["password"],
        },
    )
    # Test Case 1: Valid token
    access_token = response.json()["access_token"]
    user = get_current_user(access_token, db_session)
    assert user is not None
    assert user.username == user_payload["username"]
    assert user.email == user_payload["email"]

    # Test Case 2: Other user's token
    bad_access_token = create_access_token(data={"sub": "unauthorized_user"})
    with pytest.raises(HTTPException):
        user = get_current_user(bad_access_token, db_session)

    # Test Case 3: Expired token
    expired_token = create_access_token(
        data={"sub": user_payload["username"]},
        expires_delta=timedelta(minutes=-1),
    )
    with pytest.raises(HTTPException):
        user = get_current_user(expired_token, db_session)

    # Test Case 4: Blacklisted token
    response = test_client.post(
        logout_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    with pytest.raises(HTTPException):
        user = get_current_user(access_token, db_session)
