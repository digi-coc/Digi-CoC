from uuid import UUID

from sqlalchemy.orm import Session

from app.models.unauthorized_attempts import UnauthorizedAttempt


def record_unauthorized_attempt(
    db: Session,
    attempt_type: str,
    reason: str,
    evidence_id: UUID | None = None,
    personnel_id: UUID | None = None,
) -> UnauthorizedAttempt:
    """
    Record an unauthorized attempt.

    The caller is responsible for committing the transaction.
    """

    attempt = UnauthorizedAttempt(
        evidence_id=evidence_id,
        personnel_id=personnel_id,
        attempt_type=attempt_type,
        reason=reason,
    )

    db.add(attempt)

    return attempt
