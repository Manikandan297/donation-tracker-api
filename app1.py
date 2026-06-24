from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, get_db
from models import Transaction
from schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    UserSummaryResponse,
    RankingResponse,
    MessageResponse,
)

# ─── App Initialisation ───────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Donation API",
    description="A FastAPI backend for managing donation transactions with idempotency support.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post(
    "/transaction",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
    tags=["Transactions"],
)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new donation transaction.

    - **Idempotent**: If the same `request_id` is submitted again, a 409 Conflict is returned.
    - **amount** must be greater than 0.
    - **user_id** must be greater than 0.
    """
    existing = db.query(Transaction).filter(
        Transaction.request_id == transaction.request_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction with request_id '{transaction.request_id}' already exists.",
        )

    new_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        request_id=transaction.request_id,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@app.get(
    "/transactions",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all transactions (paginated)",
    tags=["Transactions"],
)
def get_transactions(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of results per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all transactions with pagination.

    - **page**: Page number starting from 1.
    - **page_size**: Records per page (max 100).
    """
    total = db.query(func.count(Transaction.id)).scalar()

    offset = (page - 1) * page_size
    transactions = (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=transactions,
    )


@app.get(
    "/transaction/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single transaction by ID",
    tags=["Transactions"],
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific transaction by its primary key ID.
    Returns 404 if the transaction is not found.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found.",
        )

    return transaction


@app.get(
    "/transactions/user/{user_id}",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions for a specific user (paginated)",
    tags=["Transactions"],
)
def get_user_transactions(
    user_id: int,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of results per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all transactions for a specific user, with pagination.
    """
    total = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.user_id == user_id)
        .scalar()
    )

    offset = (page - 1) * page_size
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=transactions,
    )


@app.get(
    "/summary/{user_id}",
    response_model=UserSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get donation summary for a user",
    tags=["Summary"],
)
def get_summary(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the total donation amount and transaction count for a specific user.
    """
    result = (
        db.query(
            func.count(Transaction.id).label("transaction_count"),
            func.coalesce(func.sum(Transaction.amount), 0.0).label("total_amount"),
        )
        .filter(Transaction.user_id == user_id)
        .one()
    )

    return UserSummaryResponse(
        user_id=user_id,
        transaction_count=result.transaction_count,
        total_amount=result.total_amount,
    )


@app.get(
    "/ranking",
    response_model=list[RankingResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user ranking based on donations",
    tags=["Summary"],
)
def get_ranking(
    limit: int = Query(default=10, ge=1, le=100, description="Top N users to return"),
    db: Session = Depends(get_db),
):
    """
    Get a ranking of users based on a multi-factor score.
    
    The score is calculated as:
    `Score = (Total Amount * 0.8) + (Transaction Count * 20)`
    
    This ensures that both the total volume of money donated and the frequency
    of donations contribute to the user's final rank.
    """
    results = (
        db.query(
            Transaction.user_id,
            func.count(Transaction.id).label("transaction_count"),
            func.coalesce(func.sum(Transaction.amount), 0.0).label("total_amount"),
        )
        .group_by(Transaction.user_id)
        .all()
    )

    ranking_data = []
    for row in results:
        # Score calculation based on more than one factor
        score = (row.total_amount * 0.8) + (row.transaction_count * 20.0)
        ranking_data.append({
            "user_id": row.user_id,
            "total_amount": row.total_amount,
            "transaction_count": row.transaction_count,
            "score": score
        })

    # Sort descending by score
    ranking_data.sort(key=lambda x: x["score"], reverse=True)

    # Assign rank and limit
    final_response = []
    for idx, data in enumerate(ranking_data[:limit]):
        data["rank"] = idx + 1
        final_response.append(RankingResponse(**data))

    return final_response


@app.delete(
    "/transaction/{transaction_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a transaction by ID",
    tags=["Transactions"],
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a specific transaction by its ID.
    Returns 404 if the transaction is not found.
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found.",
        )

    db.delete(transaction)
    db.commit()

    return MessageResponse(message=f"Transaction {transaction_id} deleted successfully.")


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    tags=["Health"],
)
def health_check():
    """Simple health check to verify the API is running."""
    return {"status": "ok", "message": "Donation API is running."}