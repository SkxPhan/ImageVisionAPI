import pytest


@pytest.mark.api
@pytest.mark.integration
def test_register(test_client, user_payload, register_endpoint):
    response = test_client.post(
        register_endpoint,
        json=user_payload,
    )

    assert response.status_code == 201
    response_data = response.json()

    assert response_data["status"] == "Success"
    assert response_data["message"] == "User JohnDoe registered successfully."

    # check that the user has been saved into the db
