from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustodyEventCreate(BaseModel):
    evidence_id: UUID
    to_personnel_id: UUID
    access_request_id: UUID
    device_id: UUID | None = None
    biometric_verification_id: UUID | None = None

    transfer_reason: str = Field(
        min_length=3,
        max_length=250,
    )

    location: str | None = Field(
        default=None,
        max_length=250,
    )

    verification_method: str | None = Field(
        default=None,
        max_length=50,
    )


class CustodyCorrectionCreate(BaseModel):
    correction_reason: str = Field(
        min_length=10,
        max_length=1000,
    )


class CustodyEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    performed_by_personnel_id: UUID | None
    from_personnel_id: UUID | None
    to_personnel_id: UUID
    device_id: UUID | None
    access_request_id: UUID | None
    biometric_verification_id: UUID | None
    transfer_reason: str
    location: str | None
    verification_method: str
    event_time: datetime
    previous_hash: str | None
    event_hash: str | None
    corrects_event_id: UUID | None
    correction_reason: str | None


class CustodyIntegrityResponse(BaseModel):
    evidence_id: UUID
    valid: bool
    event_count: int
    broken_event_id: UUID | None = None
    message: str


class CustodyCorrectionResponse(BaseModel):
    message: str
    original_event_id: UUID
    correction_event: CustodyEventResponse
