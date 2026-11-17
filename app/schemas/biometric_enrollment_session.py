
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


FingerPosition = Literal[
    "right_thumb",
    "right_index",
    "right_middle",
    "right_ring",
    "right_little",
    "left_thumb",
    "left_index",
    "left_middle",
    "left_ring",
    "left_little",
]


class BiometricEnrollmentSessionCreate(BaseModel):
    personnel_id: UUID
    device_id: UUID
    finger_position: FingerPosition


class BiometricEnrollmentSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    personnel_id: UUID
    organization_id: UUID
    device_id: UUID
    finger_position: str
    status: str
    expires_at: datetime
    completed_at: datetime | None
    created_at: datetime


class BiometricEnrollmentSessionProvisionResponse(
    BiometricEnrollmentSessionResponse
):
    session_token: str
    message: str


class BiometricEnrollmentSessionCancelResponse(BaseModel):
    success: bool
    session_id: UUID
    message: str
