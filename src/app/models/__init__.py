from app.database import Base

from .mortgage import MortgageOrm  # noqa: F401
from .property import PropertyOrm  # noqa: F401

__all__ = ["Base"]
