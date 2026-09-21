from typing import Any

from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    case_id: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    reason: str = Field(default="")
    approval_route: str | None = None


class ActionResponse(BaseModel):
    case_id: str
    action: str
    reason: str
    status: str
    execution_status: str | None = None
    approval_id: str | None = None
    policy: dict[str, Any] | None = None