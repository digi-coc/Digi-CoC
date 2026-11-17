from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UnauthorizedAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID | None
    personnel_id: UUID | None
    attempt_type: str
    reason: str
    attempted_at: datetime