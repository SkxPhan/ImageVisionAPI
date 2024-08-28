from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class UserORM(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    creationdate = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedate = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )

    images = relationship("ImageORM", back_populates="user")
