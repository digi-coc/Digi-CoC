
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, EmailStr


class OrganizationCreate(BaseModel):
    """Fields required to register an organization."""

    name: str = Field(min_length=2, max_length=150)
    organization_code: str = Field(min_length=2, max_length=50)
    address: str | None = Field(default=None, max_length=300)
    contact_email: EmailStr | None = None


class OrganizationResponse(BaseModel):
    """Fields returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    organization_code: str
    address: str | None
    contact_email: str | None
    status: str
    created_at: datetime
    updated_at: datetime
