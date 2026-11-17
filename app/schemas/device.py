
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


DeviceType = Literal[
    "ESP32_CONTROLLER",
    "FINGERPRINT_SENSOR",
    "RFID_READER",
    "NFC_READER",
    "OTHER",
]


class DeviceCreate(BaseModel):
    organization_id: UUID
    device_code: str = Field(min_length=1, max_length=100)
    device_type: DeviceType
    description: str | None = Field(default=None, max_length=250)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    device_code: str
    device_type: str
    description: str | None
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DeviceProvisionResponse(DeviceResponse):
    # Display this key once when a device is registered or rotated.
    api_key: str


class DeviceKeyRotationResponse(BaseModel):
    device_id: UUID
    device_code: str
    api_key: str
    message: str


class DeviceScanRequest(BaseModel):
    tag_identifier: str = Field(min_length=1, max_length=255)
    scan_type: Literal["RFID", "NFC"]


class DeviceScanResponse(BaseModel):
    success: bool
    message: str
    evidence_id: UUID | None = None
    evidence_code: str | None = None
    item_name: str | None = None
