import uuid

from sqlalchemy import TIMESTAMP, Column, LargeBinary, Numeric, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from app.database import Base


class ImageORM(Base):
    __tablename__ = "image"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    classification = Column(String(255), nullable=True)
    probability = Column(Numeric(5, 4), nullable=True)

    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )
