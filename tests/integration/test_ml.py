import io

import pytest

import app.models as models
from app.main import ml_models


@pytest.fixture(scope="function")
def image_file(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return {"file": ("test_image.png", buf)}


@pytest.fixture(scope="function")
def mock_image_classifier(monkeypatch):
    class MockImageClassifier:
        def predict_category(self, image):
            return "mock_category", 0.99

    monkeypatch.setitem(ml_models, "image_classifier", MockImageClassifier())


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
    test_client, predict_endpoint, image_file, db_session, mock_image_classifier
):
    response = test_client.post(
        predict_endpoint,
        files=image_file,
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["status"] == "Success"
    assert response_data["results"]["filename"] == "test_image.png"
    assert response_data["results"]["width"] == 400
    assert response_data["results"]["height"] == 400
    assert response_data["results"]["prediction"] == "mock_category"
    assert response_data["results"]["probability"] == 0.99

    image = (
        db_session.query(models.ImageORM)
        .filter_by(filename="test_image.png")
        .first()
    )
    assert image is not None
    assert image.classification == "mock_category"
