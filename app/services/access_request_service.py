from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.access_requests import AccessRequest
from app.services.authorization import evaluate_access_request
from app.services.audit_service import record_audit_event
from app.services.security_service import record_unauthorized_attempt


def check_access_request(
    db: Session,
    evidence_id: UUID,
    personnel_id: UUID,
    device_id: UUID | None = None,
    correlation_id: str | None = None,
) -> dict:
    """Check eligibility without granting access or authorizing a transfer."""

    allowed, reason = evaluate_access_request(
        db=db,
        evidence_id=evidence_id,
        personnel_id=personnel_id,
        device_id=device_id,
    )

    if allowed:
        record_audit_event(
            db=db,
            action="ACCESS_ELIGIBILITY_CHECK",
            resource_type="evidence",
            resource_id=evidence_id,
            personnel_id=personnel_id,
            outcome="eligible",
            details=reason,
            correlation_id=correlation_id,
        )
    else:
        record_unauthorized_attempt(
            db=db,
            evidence_id=evidence_id,
            personnel_id=personnel_id,
            attempt_type="ACCESS_REQUEST",
            reason=reason,
        )

        record_audit_event(
            db=db,
            action="ACCESS_ELIGIBILITY_CHECK",
            resource_type="evidence",
            resource_id=evidence_id,
            personnel_id=personnel_id,
            outcome="denied",
            details=reason,
            correlation_id=correlation_id,
        )

    db.commit()

    return {
        "eligible": allowed,
        "reason": reason,
        "evidence_id": str(evidence_id),
        "personnel_id": str(personnel_id),
        "device_id": str(device_id) if device_id else None,
        "correlation_id": correlation_id,
    }


def decide_access_request(
    db: Session,
    request_id: UUID,
    reviewer_personnel_id: UUID,
    decision: str,
    decision_reason: str,
) -> AccessRequest:
    """
    Approve or reject a pending request.

    IMPORTANT: The caller must authenticate the reviewer and verify their
    permission before calling this function.
    """

    decision = decision.strip().lower()
    decision_reason = decision_reason.strip()

    if decision not in {"approved", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Decision must be 'approved' or 'rejected'.",
        )

    if not decision_reason:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A decision reason is required.",
        )

    try:
        request = (
            db.query(AccessRequest)
            .filter(AccessRequest.id == request_id)
            .with_for_update()
            .first()
        )

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Access request not found.",
            )

        if request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This request has already been reviewed.",
            )

        if request.personnel_id == reviewer_personnel_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A requester cannot review their own request.",
            )

        reviewer = db.get(
            __import__("app.models.personnel", fromlist=["Personnel"]).Personnel,
            reviewer_personnel_id,
        )

        if reviewer is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Reviewer personnel record not found.",
            )

        request.status = decision
        request.reviewed_by_personnel_id = reviewer_personnel_id
        request.decision_reason = decision_reason
        request.decided_at = datetime.now(timezone.utc)

        record_audit_event(
            db=db,
            action="ACCESS_REQUEST_DECISION",
            resource_type="access_request",
            resource_id=request.id,
            personnel_id=reviewer_personnel_id,
            outcome=decision,
            details=decision_reason,
            correlation_id=request.correlation_id,
        )

        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise