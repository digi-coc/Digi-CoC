from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    """Fields required to create an investigation case."""

    organization_id: UUID
    case_code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    case_type: str = Field(min_length=1, max_length=100)


class CaseResponse(BaseModel):
    """Fields returned by the Cases API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    case_code: str
    title: str
    case_type: str
    status: str
    created_at: datetime
    updated_at: datetime
