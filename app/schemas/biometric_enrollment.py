
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BiometricEnrollmentCreate(BaseModel):
    personnel_id: UUID
    device_id: UUID

    template_reference: str = Field(
        min_length=1,
        max_length=100,
    )


class BiometricEnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    personnel_id: UUID
    device_id: UUID
    template_reference: str
    enrollment_status: str
    enrolled_at: datetime
    revoked_at: datetime | None
    created_at: datetime
