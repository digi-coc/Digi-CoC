
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.evidence_tags import EvidenceTag
from app.models.personnel import Personnel
from app.services.audit_service import record_audit_event
from app.services.evidence_service import get_evidence_for_personnel


def register_tag(
    db: Session,
    evidence_id: UUID,
    tag_type: str,
    tag_identifier: str,
    personnel: Personnel,
) -> EvidenceTag:
    # Confirm that the evidence belongs to this organisation.
    get_evidence_for_personnel(
        db=db,
        evidence_id=evidence_id,
        personnel=personnel,
    )

    normalized_identifier = tag_identifier.strip().upper()

    if not normalized_identifier:
        raise HTTPException(
            status_code=422,
            detail="Tag identifier cannot be empty.",
        )

    existing_tag = db.scalar(
        select(EvidenceTag).where(
            EvidenceTag.tag_identifier == normalized_identifier
        )
    )

    if existing_tag is not None:
        raise HTTPException(
            status_code=409,
            detail="This tag identifier is already registered.",
        )

    tag = EvidenceTag(
        evidence_id=evidence_id,
        tag_type=tag_type,
        tag_identifier=normalized_identifier,
    )

    db.add(tag)

    try:
        db.flush()

        record_audit_event(
            db=db,
            action="EVIDENCE_TAG_REGISTERED",
            resource_type="evidence_tag",
            resource_id=tag.id,
            personnel_id=personnel.id,
            outcome="success",
            details=(
                f"{tag_type} tag {normalized_identifier} "
                f"assigned to evidence {evidence_id}."
            ),
        )

        db.commit()
        db.refresh(tag)

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Tag registration failed due to a database constraint.",
        ) from exc

    return tag


def list_tags_for_evidence(
    db: Session,
    evidence_id: UUID,
    personnel: Personnel,
    active_only: bool = True,
) -> list[EvidenceTag]:
    get_evidence_for_personnel(
        db=db,
        evidence_id=evidence_id,
        personnel=personnel,
    )

    query = select(EvidenceTag).where(
        EvidenceTag.evidence_id == evidence_id
    )

    if active_only:
        query = query.where(EvidenceTag.is_active.is_(True))

    query = query.order_by(EvidenceTag.created_at.desc())

    return list(db.scalars(query).all())


def lookup_tag(
    db: Session,
    tag_identifier: str,
    personnel: Personnel,
) -> EvidenceTag:
    normalized_identifier = tag_identifier.strip().upper()

    tag = db.scalar(
        select(EvidenceTag).where(
            EvidenceTag.tag_identifier == normalized_identifier
        )
    )

    if tag is None or not tag.is_active:
        record_audit_event(
            db=db,
            action="EVIDENCE_TAG_LOOKUP_FAILED",
            resource_type="evidence_tag",
            personnel_id=personnel.id,
            outcome="denied",
            details=f"Unknown or inactive tag: {normalized_identifier}",
        )
        db.commit()

        raise HTTPException(
            status_code=404,
            detail="Tag was not found or is inactive.",
        )

    # This also checks that the evidence belongs to the user's organisation.
    get_evidence_for_personnel(
        db=db,
        evidence_id=tag.evidence_id,
        personnel=personnel,
    )

    record_audit_event(
        db=db,
        action="EVIDENCE_TAG_LOOKUP",
        resource_type="evidence_tag",
        resource_id=tag.id,
        personnel_id=personnel.id,
        outcome="success",
        details=f"Tag {normalized_identifier} looked up successfully.",
    )

    db.commit()
    db.refresh(tag)

    return tag


def deactivate_tag(
    db: Session,
    tag_id: UUID,
    personnel: Personnel,
) -> EvidenceTag:
    tag = db.get(EvidenceTag, tag_id)

    if tag is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence tag was not found.",
        )

    get_evidence_for_personnel(
        db=db,
        evidence_id=tag.evidence_id,
        personnel=personnel,
    )

    if not tag.is_active:
        raise HTTPException(
            status_code=409,
            detail="This tag is already inactive.",
        )

    tag.is_active = False

    record_audit_event(
        db=db,
        action="EVIDENCE_TAG_DEACTIVATED",
        resource_type="evidence_tag",
        resource_id=tag.id,
        personnel_id=personnel.id,
        outcome="success",
        details=f"Tag {tag.tag_identifier} was deactivated.",
    )

    db.commit()
    db.refresh(tag)

    return tag
