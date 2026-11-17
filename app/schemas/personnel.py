from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PersonnelCreate(BaseModel):
    organization_id: UUID
    personnel_code: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=100)


class PersonnelUpdate(BaseModel):
    full_name: str | None = Field(
        default=None, min_length=1, max_length=200
    )
    role: str | None = Field(
        default=None, min_length=1, max_length=100
    )


class PersonnelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    personnel_code: str
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime