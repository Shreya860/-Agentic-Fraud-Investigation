from fastapi import APIRouter, HTTPException
from api.schemas.case import CaseCreateRequest, CaseResponse
from cases.case_manager import get_case_manager


router = APIRouter(
    prefix="/cases",
    tags=["Cases"],
)

case_manager = get_case_manager()


@router.post(
    "",
    response_model=CaseResponse,
)
def create_case(request: CaseCreateRequest):
    try:
        return case_manager.create_case(
            customer_id=request.customer_id,
            trigger_type=request.trigger_type,
            trigger_text=request.trigger_text,
            flagged_txn_id=request.flagged_txn_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
)
def get_case(case_id: str):
    try:
        case = case_manager.get_case(case_id)

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case not found: {case_id}",
            )

        return case

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc