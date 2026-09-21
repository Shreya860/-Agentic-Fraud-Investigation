from typing import Any

from pydantic import BaseModel, Field


class CaseCreateRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    trigger_type: str = Field(default="analyst_request")
    trigger_text: str = Field(default="")
    flagged_txn_id: str | None = None


class CaseResponse(BaseModel):
    case_id: str
    customer_id: str
    status: str
    risk_level: str
    findings: list[Any]
    evidence: list[Any]
    decisions: list[Any]
    actions: list[Any]
    approval_requests: list[Any]
    created_at: str
    updated_at: str
    closed_at: str | None = None