import bcrypt
import pytest

import app.models as models
from app.database import TokenBlacklistORM


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
