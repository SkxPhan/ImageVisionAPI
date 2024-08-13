import uuid

from sqlalchemy import TIMESTAMP, Column, LargeBinary, String
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from app.database import Base


class ImageORM(Base):
    __tablename__ = "image"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    image_data = Column(LargeBinary, nullable=False)

    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )
