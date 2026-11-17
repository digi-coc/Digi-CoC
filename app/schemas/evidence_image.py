from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceImageCreate(BaseModel):
    evidence_id: UUID

    storage_key: str = Field(
        min_length=1,
        max_length=500,
    )

    original_filename: str = Field(
        min_length=1,
        max_length=255,
    )

    content_type: str = Field(
        min_length=1,
        max_length=100,
    )

    file_size_bytes: int = Field(gt=0)

    sha256_hash: str = Field(
        pattern=r"^[a-fA-F0-9]{64}$",
    )


class EvidenceImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    storage_key: str
    original_filename: str
    content_type: str
    file_size_bytes: int
    sha256_hash: str
    uploaded_at: datetime