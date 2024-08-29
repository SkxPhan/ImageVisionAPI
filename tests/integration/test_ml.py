import io

import pytest

import app.models as models
from app.core.setup import ml_models


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
@pytest.mark.integration
def test_predict(
    test_client,
    predict_endpoint,
    image_file,
    db_session,
    access_token,
    mock_image_classifier,
):
    # Test Case 1: Without authentication
    response = test_client.post(
        predict_endpoint,
        files=image_file,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

    # Test Case 2: With authentication
    response = test_client.post(
        predict_endpoint,
        files=image_file,
        headers={"Authorization": f"Bearer {access_token}"},
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
    assert image.label == "mock_category"
    assert image.user_id == 1
