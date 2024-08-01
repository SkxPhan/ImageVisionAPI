import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from image_vision_ai.app.main import app, ml_models


class MockImageClassifier:
    def predict_category(self, image):
        return "mock_category", 0.99


@pytest.fixture(scope="function")
def test_client():
    """Create a test client."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def image_file():
    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf, "test_image.png"


@pytest.fixture(scope="function")
def mock_image_classifier():
    ml_models["image_classifier"] = MockImageClassifier()
    yield
    ml_models.clear()
