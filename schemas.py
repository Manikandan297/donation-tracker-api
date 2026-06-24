from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List


# ─── Request Schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""

    user_id: int = Field(..., gt=0, description="ID of the user making the donation")
    amount: float = Field(..., gt=0, description="Donation amount (must be greater than 0)")
    request_id: str = Field(..., min_length=1, description="Unique idempotency key for this transaction")

    @field_validator("request_id")
    @classmethod
    def request_id_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("request_id must not be blank or whitespace")
        return v.strip()


# ─── Response Schemas ─────────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    """Schema for returning a single transaction."""

    id: int
    user_id: int
    amount: float
    request_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    """Schema for a paginated list of transactions."""

    total: int
    page: int
    page_size: int
    transactions: List[TransactionResponse]


class UserSummaryResponse(BaseModel):
    """Schema for returning a user's donation summary."""

    user_id: int
    transaction_count: int
    total_amount: float


class RankingResponse(BaseModel):
    """Schema for returning a user's ranking."""
    
    user_id: int
    total_amount: float
    transaction_count: int
    score: float
    rank: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str