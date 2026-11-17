
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_personnel, require_roles
from app.database.connections import get_db
from app.models.cases import Case
from app.models.evidence import Evidence
from app.models.personnel import Personnel
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceStatusUpdate,
    EvidenceUpdate,
)
from app.services.evidence_service import (
    change_evidence_status,
    create_evidence as register_evidence,
    get_evidence_for_personnel,
    update_evidence as edit_evidence,
)


router = APIRouter(
    prefix="/api/evidence",
    tags=["Evidence"],
)


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence(
    payload: EvidenceCreate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    try:
        return register_evidence(
            db=db,
            payload=payload,
            personnel=current_personnel,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Evidence could not be created. "
                "Check whether the evidence code already exists "
                "for this case."
            ),
        ) from exc


@router.get(
    "",
    response_model=list[EvidenceResponse],
)
def list_evidence(
    case_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    query = (
        select(Evidence)
        .join(Case, Evidence.case_id == Case.id)
        .where(
            Case.organization_id == current_personnel.organization_id
        )
    )

    if case_id is not None:
        query = query.where(Evidence.case_id == case_id)

    query = (
        query
        .order_by(Evidence.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    return get_evidence_for_personnel(
        db=db,
        evidence_id=evidence_id,
        personnel=current_personnel,
    )


@router.patch(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def update_evidence(
    evidence_id: UUID,
    payload: EvidenceUpdate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    changes = payload.model_dump(exclude_unset=True)

    try:
        return edit_evidence(
            db=db,
            evidence_id=evidence_id,
            changes=changes,
            personnel=current_personnel,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Evidence could not be updated.",
        ) from exc


@router.patch(
    "/{evidence_id}/status",
    response_model=EvidenceResponse,
)
def update_evidence_status(
    evidence_id: UUID,
    payload: EvidenceStatusUpdate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
):
    try:
        return change_evidence_status(
            db=db,
            evidence_id=evidence_id,
            new_status=payload.status,
            personnel=current_personnel,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Evidence status could not be updated.",
        ) from exc
