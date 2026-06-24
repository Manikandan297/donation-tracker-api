from database import Base
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func


class Transaction(Base):
    """SQLAlchemy ORM model representing a donation transaction."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    request_id = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)