from fastapi import APIRouter, HTTPException
from api.schemas.action import ActionRequest, ActionResponse
from cases.case_manager import get_case_manager
from policy.permissions import PermissionEngine

router = APIRouter(
    prefix="/actions",
    tags=["Actions"],
)

case_manager = get_case_manager()
permission_engine = PermissionEngine()


@router.post(
    "/authorize",
    response_model=ActionResponse,
)
def authorize_action(request: ActionRequest):
    try:
        case = case_manager.get_case(request.case_id)

        if case is None:
            raise HTTPException(
                status_code=404,
                detail=f"Case not found: {request.case_id}",
            )

        decision = {
            "action": request.action,
            "reason": request.reason,
            "approval_route": request.approval_route,
        }

        authorized = permission_engine.authorize_decision(decision)

        policy = authorized.get("policy", {})
        policy_status = authorized.get(
            "policy_status",
            "unknown",
        )
        execution_status = authorized.get(
            "execution_status",
            policy_status,
        )

        return {
            "case_id": request.case_id,
            "action": request.action,
            "reason": request.reason,
            "status": policy_status,
            "execution_status": execution_status,
            "approval_id": None,
            "policy": policy,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc