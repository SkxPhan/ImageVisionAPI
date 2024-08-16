from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, TokenBlacklistORM

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.mark.integration
def test_create_token_blacklist(db_session):
    token = "testtoken123"
    expires_at = datetime.now()

    new_token = TokenBlacklistORM(token=token, expires_at=expires_at)
    db_session.add(new_token)
    db_session.commit()

    result = db_session.query(TokenBlacklistORM).filter_by(token=token).first()
    assert result is not None
    assert result.token == token
    assert result.expires_at == expires_at
