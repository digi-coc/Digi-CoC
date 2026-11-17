
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_personnel
from app.database.connections import get_db
from app.models.personnel import Personnel
from app.schemas.evidence_tag import (
    EvidenceTagCreate,
    EvidenceTagLookupResponse,
    EvidenceTagResponse,
)
from app.services.evidence_tag_service import (
    deactivate_tag,
    list_tags_for_evidence,
    lookup_tag,
    register_tag,
)


router = APIRouter(
    prefix="/api/evidence-tags",
    tags=["Evidence Tags"],
)


@router.post(
    "",
    response_model=EvidenceTagResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_tag(
    payload: EvidenceTagCreate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    return register_tag(
        db=db,
        evidence_id=payload.evidence_id,
        tag_type=payload.tag_type,
        tag_identifier=payload.tag_identifier,
        personnel=current_personnel,
    )


@router.get(
    "/by-evidence/{evidence_id}",
    response_model=list[EvidenceTagResponse],
)
def get_tags_for_evidence(
    evidence_id: UUID,
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    return list_tags_for_evidence(
        db=db,
        evidence_id=evidence_id,
        personnel=current_personnel,
        active_only=active_only,
    )


@router.get(
    "/lookup/{tag_identifier}",
    response_model=EvidenceTagLookupResponse,
)
def scan_tag_lookup(
    tag_identifier: str,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    tag = lookup_tag(
        db=db,
        tag_identifier=tag_identifier,
        personnel=current_personnel,
    )

    return EvidenceTagLookupResponse(
        found=True,
        tag=tag,
        message="Active tag found and linked to evidence.",
    )


@router.patch(
    "/{tag_id}/deactivate",
    response_model=EvidenceTagResponse,
)
def deactivate_evidence_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    return deactivate_tag(
        db=db,
        tag_id=tag_id,
        personnel=current_personnel,
    )
