import pytest
from fastapi.testclient import TestClient

from image_vision_ai.app.main import app


@pytest.fixture(scope="function")
def test_client():
    """Create a test client."""

    with TestClient(app) as test_client:
        yield test_client
