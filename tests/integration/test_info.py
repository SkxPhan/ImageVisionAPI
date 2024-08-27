import pytest


@pytest.mark.api
@pytest.mark.integration
def test_healthchecker(test_client, healthchecker_endpoint):
    response = test_client.get(healthchecker_endpoint)
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!"}


@pytest.mark.api
@pytest.mark.integration
def test_show_about(test_client, about_endpoint):
    response = test_client.get(about_endpoint)
    assert response.status_code == 200
