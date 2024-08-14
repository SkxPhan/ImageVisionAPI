from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class UserORM(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    creationdate = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedate = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )
