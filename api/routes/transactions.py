from fastapi import APIRouter, HTTPException

from tools.transaction_tools import TransactionTools


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

transaction_tools = TransactionTools()


@router.get("/{transaction_id}")
def get_transaction(transaction_id: str):
    try:
        transaction = transaction_tools.get_transaction(
            transaction_id
        )

        if transaction is None:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction not found: {transaction_id}",
            )

        return transaction

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/customer/{customer_id}")
def get_customer_transactions(
    customer_id: str,
    limit: int = 10,
):
    try:
        return transaction_tools.get_customer_transactions(
            customer_id=customer_id,
            limit=limit,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc