import uuid
from enum import Enum

from sqlalchemy import TIMESTAMP, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from app.database import Base


class MortgageType(str, Enum):
    interest_only = "interest_only"
    repayment = "repayment"


class MortgageOrm(Base):
    __tablename__ = "mortgage"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUIDType(binary=False), ForeignKey("property.id"))
    loan_to_value = Column(Numeric(5, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)
    mortgage_type = Column(SQLAlchemyEnum(MortgageType), nullable=False)
    loan_term = Column(Numeric(5, 2), nullable=True)
    mortgage_amount = Column(Numeric(10, 2), nullable=False)

    property = relationship("PropertyOrm", back_populates="mortgages")

    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updatedAt = Column(
        TIMESTAMP(timezone=True), default=None, onupdate=func.now()
    )
