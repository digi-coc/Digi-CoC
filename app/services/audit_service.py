from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_logs import AuditLog


def record_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    outcome: str,
    personnel_id: UUID | None = None,
    resource_id: UUID | None = None,
    details: str | None = None,
    correlation_id: str | None = None,
) -> AuditLog:
    """
    Add an audit event to the current database transaction.

    The caller is responsible for committing the transaction.
    """

    audit_event = AuditLog(
        personnel_id=personnel_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        details=details,
        correlation_id=correlation_id,
    )

    db.add(audit_event)

    return audit_event