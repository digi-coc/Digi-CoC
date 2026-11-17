from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCreate(BaseModel):
    case_id: UUID
    evidence_code: str = Field(min_length=1, max_length=50)
    item_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    evidence_category: str = Field(min_length=1, max_length=100)


class EvidenceUpdate(BaseModel):
    item_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    evidence_category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class EvidenceStatusUpdate(BaseModel):
    # Custody-specific statuses are deliberately excluded.
    status: Literal["collected", "released", "archived"]


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    evidence_code: str
    item_name: str
    description: str | None
    evidence_category: str
    status: str
    created_at: datetime
    updated_at: datetime
