from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database_old import get_db
from app.models.audit_logs import AuditLog
from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[AuditLogResponse],
)
def list_audit_logs(
    personnel_id: UUID | None = Query(default=None),
    resource_type: str | None = Query(default=None, max_length=100),
    outcome: str | None = Query(default=None, max_length=30),
    correlation_id: str | None = Query(default=None, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(AuditLog)

    if personnel_id is not None:
        query = query.where(AuditLog.personnel_id == personnel_id)

    if resource_type is not None:
        query = query.where(AuditLog.resource_type == resource_type)

    if outcome is not None:
        query = query.where(AuditLog.outcome == outcome)

    if correlation_id is not None:
        query = query.where(
            AuditLog.correlation_id == correlation_id
        )

    query = (
        query.order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())