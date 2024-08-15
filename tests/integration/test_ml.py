import pytest


@pytest.mark.api
def test_healthchecker(test_client, healthchecker_endpoint):
    response = test_client.get(healthchecker_endpoint)
    assert response.status_code == 200
    assert response.json() == {"message": "The API is LIVE!"}


@pytest.mark.api
def test_show_about(test_client, about_endpoint):
    response = test_client.get(about_endpoint)
    assert response.status_code == 200


@pytest.mark.api
@pytest.mark.integration
def test_predict(
    test_client, image_file, mock_image_classifier, predict_endpoint
):
    response = test_client.post(
        predict_endpoint,
        files=image_file,
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["status"] == "Success"
    assert response_data["results"]["filename"] == "test_image.png"
    assert response_data["results"]["width"] == 100
    assert response_data["results"]["height"] == 100
    assert response_data["results"]["prediction"] == "mock_category"
    assert response_data["results"]["probability"] == 0.99

    # check that the image has been saved into the db