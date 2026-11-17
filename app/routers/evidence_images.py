from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database_old import get_db
from app.models.evidence import Evidence
from app.models.evidence_images import EvidenceImage
from app.schemas.evidence_image import (
    EvidenceImageCreate,
    EvidenceImageResponse,
)


router = APIRouter(
    prefix="/api/evidence-images",
    tags=["Evidence Images"],
)


@router.post(
    "",
    response_model=EvidenceImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence_image(
    payload: EvidenceImageCreate,
    db: Session = Depends(get_db),
):
    evidence = db.get(Evidence, payload.evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence was not found.",
        )

    image_record = EvidenceImage(**payload.model_dump())
    db.add(image_record)

    try:
        db.commit()
        db.refresh(image_record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "Image metadata could not be registered. "
                "Check the storage key and database constraints."
            ),
        ) from exc

    return image_record


@router.get(
    "/by-evidence/{evidence_id}",
    response_model=list[EvidenceImageResponse],
)
def list_evidence_images(
    evidence_id: UUID,
    db: Session = Depends(get_db),
):
    evidence = db.get(Evidence, evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence was not found.",
        )

    query = (
        select(EvidenceImage)
        .where(EvidenceImage.evidence_id == evidence_id)
        .order_by(EvidenceImage.uploaded_at.desc())
    )

    return list(db.scalars(query).all())