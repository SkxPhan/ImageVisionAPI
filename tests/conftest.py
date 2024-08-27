import os
import pathlib

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as models
from app.api.v1.auth import create_access_token, get_password_hash, get_user
from app.database import Base, get_db
from app.main import app


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


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db(db_url):
    """Create and tear down the database."""
    db_path = pathlib.Path(db_url.split("///")[-1])
    if db_path.exists():
        os.remove(db_path)

    engine = create_engine(db_url, poolclass=StaticPool, echo=True)
    Base.metadata.create_all(bind=engine)

    yield db_url

    Base.metadata.drop_all(bind=engine)
    if db_path.exists():
        os.remove(db_path)


@pytest.fixture(scope="function")
def db_session(setup_and_teardown_db):
    """Create a new database session with a rollback at the end of the test."""
    # Create a SQLAlchemy engine
    db_url = setup_and_teardown_db
    engine = create_engine(db_url, poolclass=StaticPool, echo=True)

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


@pytest.fixture(autouse=True)
def mock_init_db(monkeypatch):
    monkeypatch.setattr("app.main.init_db", lambda: None)


# --------------------------------- Fake Data ---------------------------------
@pytest.fixture
def image():
    return Image.new("RGB", (400, 400), color="red")


@pytest.fixture
def user_payload():
    return {
        "username": "JohnDoe",
        "email": "johndoe@example.com",
        "password": "password",
    }


@pytest.fixture
def user_db(user_payload, db_session):
    hashed_password = get_password_hash(user_payload["password"])
    new_user = models.UserORM(
        username=user_payload["username"],
        email=user_payload["email"],
        hashed_password=hashed_password,
    )
    db_session.add(new_user)
    db_session.commit()
    return get_user(user_payload["username"], db_session)


@pytest.fixture
def access_token(user_payload, user_db):
    return create_access_token(data={"sub": user_payload["username"]})


# ------------------------------- API Endpoints -------------------------------
@pytest.fixture
def healthchecker_endpoint():
    return "/api/v1"


@pytest.fixture
def about_endpoint():
    return "/api/v1/about"


@pytest.fixture
def predict_endpoint():
    return "/api/v1/ml/predict"


@pytest.fixture
def register_endpoint():
    return "/api/v1/auth/register"


@pytest.fixture
def login_endpoint():
    return "/api/v1/auth/login"


@pytest.fixture
def logout_endpoint():
    return "/api/v1/auth/logout"


@pytest.fixture
def read_user_me_endpoint():
    return "/api/v1/auth/users/me"


@pytest.fixture
def history_endpoint():
    return "/api/v1/auth/users/me/history"
