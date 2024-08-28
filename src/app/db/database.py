from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

from app.core.config import settings

DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_SYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: Any = declarative_base()


class TokenBlacklistORM(Base):
    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True
    )
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    with SessionLocal() as db:
        yield db
