import base64
import binascii
import re
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class BiometricTemplateEnroll(BaseModel):
    """
    Data uploaded by the authenticated ESP32.

    Personnel, organization, and finger position are deliberately
    not accepted from the device request. They are obtained from
    the admin-authorised enrollment session.
    """

    model_config = ConfigDict(extra="forbid")

    sensor_model: str = Field(
        default="R307S",
        min_length=2,
        max_length=50,
    )

    template_format: str = Field(
        min_length=1,
        max_length=100,
    )

    template_data: str = Field(
        min_length=1,
        max_length=100000,
    )

    template_checksum: str = Field(
        min_length=64,
        max_length=64,
    )

    @field_validator("sensor_model", "template_format")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("template_data")
    @classmethod
    def validate_base64(cls, value: str) -> str:
        try:
            decoded = base64.b64decode(
                value,
                validate=True,
            )
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                "Template data must be valid Base64."
            ) from exc

        if not decoded:
            raise ValueError("Template data cannot be empty.")

        return value

    @field_validator("template_checksum")
    @classmethod
    def validate_checksum(cls, value: str) -> str:
        value = value.strip().lower()

        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(
                "Checksum must be a 64-character SHA-256 hexadecimal value."
            )

        return value


class BiometricTemplateEnrollResponse(BaseModel):
    success: bool
    fingerprint_id: int
    personnel_id: UUID
    finger_position: str
    message: str


class BiometricTemplateMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fingerprint_id: int
    personnel_id: UUID
    organization_id: UUID
    finger_position: str
    sensor_model: str
    template_format: str
    is_active: bool
    enrolled_at: datetime
    revoked_at: datetime | None
    created_at: datetime


class BiometricTemplateDeviceResponse(BaseModel):
    fingerprint_id: int
    personnel_id: UUID
    template_format: str
    template_data: str
    template_checksum: str


class BiometricTemplateRevokeResponse(BaseModel):
    success: bool
    fingerprint_id: int
    message: str