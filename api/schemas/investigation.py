from typing import Any

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class InvestigationResponse(BaseModel):
    customer_id: str
    case_id: str
    investigation: dict[str, Any]
    assessment: dict[str, Any]
    memory: dict[str, Any]
    plan: dict[str, Any]
    decision: dict[str, Any]