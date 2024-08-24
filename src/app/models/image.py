from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ImageORM(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    classification = Column(String(255), nullable=True)
    probability = Column(Numeric(5, 4), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)

    creationdate = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedate = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )

    user = relationship("UserORM", back_populates="images")
