
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceTagCreate(BaseModel):
    evidence_id: UUID

    tag_type: Literal["RFID", "NFC"]

    tag_identifier: str = Field(
        min_length=1,
        max_length=255,
    )


class EvidenceTagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    tag_type: str
    tag_identifier: str
    is_active: bool
    assigned_at: datetime
    created_at: datetime


class EvidenceTagLookupResponse(BaseModel):
    found: bool
    tag: EvidenceTagResponse | None = None
    message: str
