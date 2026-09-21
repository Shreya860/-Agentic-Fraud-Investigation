from fastapi import APIRouter, HTTPException
from agent.orchestrator import InvestigationOrchestrator
from api.schemas.investigation import (
    InvestigationRequest,
    InvestigationResponse,
)


router = APIRouter(
    prefix="/investigations",
    tags=["Investigations"],
)

orchestrator = InvestigationOrchestrator()


@router.post(
    "/customer",
    response_model=InvestigationResponse,
)
def investigate_customer(request: InvestigationRequest):
    try:
        result = orchestrator.investigate_customer(
            customer_id=request.customer_id,
            limit=request.limit,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc