import uuid

from sqlalchemy import TIMESTAMP, Column, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from app.database import Base


class PropertyOrm(Base):
    __tablename__ = "property"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    rental_income = Column(Numeric(10, 2), nullable=False)
    renovation_cost = Column(Numeric(10, 2), nullable=False)
    property_name = Column(String(255), nullable=False)
    admin_costs = Column(Numeric(10, 2), nullable=False)
    management_fees = Column(Numeric(10, 2), nullable=False)

    mortgages = relationship("MortgageOrm", back_populates="property")

    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )
