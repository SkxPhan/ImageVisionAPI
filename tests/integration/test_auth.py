from datetime import timedelta

import bcrypt
import pytest

import app.models as models
from app.database import TokenBlacklistORM
from app.routers.auth import create_access_token, get_user


@pytest.mark.integration
def test_get_user(user_payload, db_session, user_db):
    user = get_user(user_payload["username"], db_session)
    assert user
    assert user.username == user_payload["username"]
    assert user.email == user_payload["email"]

    user = get_user("inexistent_user", db_session)
    assert user is None


@pytest.mark.api
@pytest.mark.integration
def test_register(test_client, register_endpoint, user_payload, db_session):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["status"] == "Success"
    assert (
        response_data["message"]
        == f"User {user_payload['username']} registered successfully."
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
def test_login(test_client, login_endpoint, user_payload, user_db):
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
def test_logout(test_client, logout_endpoint, access_token, db_session):
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
def test_read_user_me(
    test_client,
    read_user_me_endpoint,
    logout_endpoint,
    user_payload,
    access_token,
):

    # Test Case 1: Valid token
    response = test_client.get(
        read_user_me_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["username"] == user_payload["username"]
    assert response_data["email"] == user_payload["email"]
    assert response_data["is_active"] is True

    # Test Case 2: Other user's token
    bad_access_token = create_access_token(data={"sub": "unauthorized_user"})
    response = test_client.get(
        read_user_me_endpoint,
        headers={"Authorization": f"Bearer {bad_access_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

    # Test Case 3: Expired token
    new_token = create_access_token(
        data={"sub": user_payload["username"]},
        expires_delta=timedelta(minutes=-1),
    )
    response = test_client.get(
        read_user_me_endpoint,
        headers={"Authorization": f"Bearer {new_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"

    # Test Case 4: Blacklisting token by logging out
    response = test_client.post(
        logout_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response = test_client.get(
        read_user_me_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Token has been blacklisted, please log in again."
    )


@pytest.mark.api
@pytest.mark.integration
def test_get_history(
    test_client, history_endpoint, access_token, user_payload, db_session
):
    response = test_client.get(history_endpoint)
    assert response.status_code == 401

    images = [
        models.ImageORM(
            filename="test1.png",
            image_data=b"\x00\x01",
            label="category1",
            probability="0.2",
            user_id=1,
        ),
        models.ImageORM(
            filename="test2.png",
            image_data=b"\x04\x05",
            label="category2",
            probability="0.8",
            user_id=1,
        ),
        models.ImageORM(
            filename="test3.png",
            image_data=b"\x08\x09",
            label="category3",
            probability="0.6",
            user_id=1,
        ),
        models.ImageORM(
            filename="test4.png",
            image_data=b"\x08\x09",
            label="category3",
            probability="0.6",
            user_id=2,
        ),
    ]
    db_session.add_all(images)
    db_session.commit()

    response = test_client.get(
        history_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "Success"
    assert response_data["username"] == user_payload["username"]

    history = response_data["history"]
    assert len(history) == 3
    assert history[0]["filename"] == "test1.png"
    assert history[1]["filename"] == "test2.png"
    assert history[2]["filename"] == "test3.png"

    response = test_client.get(
        history_endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": "2"},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "Success"
    assert response_data["username"] == user_payload["username"]

    history = response_data["history"]
    assert len(history) == 2
    assert history[0]["filename"] == "test1.png"
    assert history[1]["filename"] == "test2.png"
