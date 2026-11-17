
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cases import Case
from app.models.evidence import Evidence
from app.models.personnel import Personnel
from app.services.audit_service import record_audit_event


# Status changes that do not represent a custody transfer.
ALLOWED_STATUS_TRANSITIONS = {
    "registered": {"collected"},
    "collected": set(),
    "in_custody": {"released"},
    "transferred": {"released"},
    "released": {"archived"},
    "archived": set(),
}


def get_case_for_personnel(
    db: Session,
    case_id: UUID,
    personnel: Personnel,
) -> Case:
    case = db.get(Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Case was not found.",
        )

    if case.organization_id != personnel.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access a case belonging to another organisation.",
        )

    return case


def get_evidence_for_personnel(
    db: Session,
    evidence_id: UUID,
    personnel: Personnel,
) -> Evidence:
    evidence = db.get(Evidence, evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence was not found.",
        )

    get_case_for_personnel(
        db=db,
        case_id=evidence.case_id,
        personnel=personnel,
    )

    return evidence


def create_evidence(
    db: Session,
    payload,
    personnel: Personnel,
) -> Evidence:
    get_case_for_personnel(
        db=db,
        case_id=payload.case_id,
        personnel=personnel,
    )

    evidence = Evidence(
        case_id=payload.case_id,
        evidence_code=payload.evidence_code.strip(),
        item_name=payload.item_name.strip(),
        description=payload.description,
        evidence_category=payload.evidence_category.strip(),
    )

    db.add(evidence)
    db.flush()

    record_audit_event(
        db=db,
        action="EVIDENCE_CREATED",
        resource_type="evidence",
        resource_id=evidence.id,
        personnel_id=personnel.id,
        outcome="success",
        details=f"Evidence {evidence.evidence_code} registered.",
    )

    db.commit()
    db.refresh(evidence)

    return evidence


def update_evidence(
    db: Session,
    evidence_id: UUID,
    changes: dict,
    personnel: Personnel,
) -> Evidence:
    evidence = get_evidence_for_personnel(
        db=db,
        evidence_id=evidence_id,
        personnel=personnel,
    )

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    for field, value in changes.items():
        if isinstance(value, str) and field != "description":
            value = value.strip()

        setattr(evidence, field, value)

    record_audit_event(
        db=db,
        action="EVIDENCE_UPDATED",
        resource_type="evidence",
        resource_id=evidence.id,
        personnel_id=personnel.id,
        outcome="success",
        details=f"Updated fields: {', '.join(changes.keys())}.",
    )

    db.commit()
    db.refresh(evidence)

    return evidence


def change_evidence_status(
    db: Session,
    evidence_id: UUID,
    new_status: str,
    personnel: Personnel,
) -> Evidence:
    evidence = get_evidence_for_personnel(
        db=db,
        evidence_id=evidence_id,
        personnel=personnel,
    )

    current_status = evidence.status

    allowed = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Status cannot be changed from "
                f"'{current_status}' to '{new_status}'."
            ),
        )

    evidence.status = new_status

    record_audit_event(
        db=db,
        action="EVIDENCE_STATUS_CHANGED",
        resource_type="evidence",
        resource_id=evidence.id,
        personnel_id=personnel.id,
        outcome="success",
        details=(
            f"Evidence status changed from "
            f"{current_status} to {new_status}."
        ),
    )

    db.commit()
    db.refresh(evidence)

    return evidence
