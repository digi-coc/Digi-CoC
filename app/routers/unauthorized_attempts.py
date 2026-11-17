from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database_old import get_db
from app.models.unauthorized_attempts import UnauthorizedAttempt
from app.schemas.unauthorized_attempt import (
    UnauthorizedAttemptResponse,
)


router = APIRouter(
    prefix="/api/unauthorized-attempts",
    tags=["Unauthorized Attempts"],
)


@router.get(
    "",
    response_model=list[UnauthorizedAttemptResponse],
)
def list_unauthorized_attempts(
    evidence_id: UUID | None = Query(default=None),
    personnel_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(UnauthorizedAttempt)

    if evidence_id is not None:
        query = query.where(
            UnauthorizedAttempt.evidence_id == evidence_id
        )

    if personnel_id is not None:
        query = query.where(
            UnauthorizedAttempt.personnel_id == personnel_id
        )

    query = (
        query.order_by(UnauthorizedAttempt.attempted_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())