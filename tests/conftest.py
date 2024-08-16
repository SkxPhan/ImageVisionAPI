import io
import pathlib

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app, ml_models


@pytest.fixture(autouse=True)
def mock_init_db(monkeypatch):
    monkeypatch.setattr("app.main.init_db", lambda: None)


def pytest_addoption(parser):
    parser.addoption(
        "--dburl",  # Or use: "postgresql://user:password@localhost/dbname"
        action="store",
        default=f"sqlite:///{pathlib.Path(__file__).parent}/data/test_db.db",
        help="Database URL to use for tests.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    db_url = session.config.getoption("--dburl")
    try:
        # Attempt to create an engine and connect to the database.
        engine = create_engine(db_url, poolclass=StaticPool)
        connection = engine.connect()
        connection.close()  # Close the connection after a successful connect.
        print("Database connection successful........")
    except SQLAlchemyOperationalError as e:
        print(f"Failed to connect to the database at {db_url}: {e}")
        pytest.exit(
            "Stopping tests because database connection cannot be established."
        )


@pytest.fixture(scope="session")
def db_url(request):
    """Fixture to retrieve the database URL."""
    return request.config.getoption("--dburl")


@pytest.fixture(scope="function")
def db_session(db_url):
    """Create a new database session with a rollback at the end of the test."""
    # Create a SQLAlchemy engine
    engine = create_engine(db_url, poolclass=StaticPool)

    # Create a sessionmaker to manage sessions
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    # Create tables in the database
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client with a mocked db."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def healthchecker_endpoint():
    return "/api/healthchecker"


@pytest.fixture(scope="function")
def about_endpoint():
    return "/api/about"


@pytest.fixture(scope="function")
def predict_endpoint():
    return "/api/v1/ml/predict/"


@pytest.fixture(scope="function")
def register_endpoint():
    return "/api/v1/auth/register/"


@pytest.fixture(scope="function")
def user_payload():
    return {
        "username": "JohnDoe",
        "email": "johndoe@example.com",
        "password": "password",
    }


@pytest.fixture
def image():
    return Image.new("RGB", (400, 400), color="red")


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

    original_image_classifier = ml_models.get("image_classifier")
    monkeypatch.setitem(ml_models, "image_classifier", MockImageClassifier())

    yield

    if original_image_classifier:
        monkeypatch.setitem(
            ml_models, "image_classifier", original_image_classifier
        )
    else:
        ml_models.pop("image_classifier", None)
