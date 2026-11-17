
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BiometricDeviceVerificationCreate(BaseModel):
    fingerprint_id: int | None = Field(
        default=None,
        ge=1,
    )

    result: Literal["success", "failed", "error"]

    correlation_id: str | None = Field(
        default=None,
        max_length=100,
    )


class BiometricVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    personnel_id: UUID | None
    device_id: UUID | None
    verification_method: str
    result: str
    correlation_id: str | None
    verified_at: datetime
