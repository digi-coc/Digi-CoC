from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    personnel_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    outcome: str
    details: str | None
    correlation_id: str | None
    created_at: datetime