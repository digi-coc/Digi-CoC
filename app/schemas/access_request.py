from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccessRequestCreate(BaseModel):
    evidence_id: UUID
    personnel_id: UUID
    device_id: UUID | None = None

    request_reason: str = Field(
        min_length=1,
        max_length=1000,
    )

    correlation_id: str | None = Field(
        default=None,
        max_length=100,
    )


class AccessRequestDecision(BaseModel):
    decision: str = Field(
        pattern=r"^(approved|rejected)$",
    )

    decision_reason: str = Field(
        min_length=1,
        max_length=1000,
    )


class AccessRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    personnel_id: UUID
    device_id: UUID | None
    request_reason: str
    status: str
    correlation_id: str | None
    created_at: datetime
    updated_at: datetime