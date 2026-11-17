from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cases import Case
from app.models.devices import Device
from app.models.evidence import Evidence
from app.models.personnel import Personnel


def evaluate_access_request(
    db: Session,
    evidence_id,
    personnel_id,
    device_id=None,
) -> tuple[bool, str]:
    """
    Perform basic eligibility checks for an evidence-access request.

    This function does not verify identity or approve a custody transfer.
    """

    evidence = db.get(Evidence, evidence_id)

    if evidence is None:
        return False, "Evidence record not found"

    personnel = db.get(Personnel, personnel_id)

    if personnel is None:
        return False, "Personnel record not found"

    case = db.get(Case, evidence.case_id)

    if case is None:
        return False, "Associated case not found"

    if personnel.organization_id != case.organization_id:
        return False, "Personnel does not belong to the case organization"

    if device_id is not None:
        device = db.get(Device, device_id)

        if device is None:
            return False, "Device record not found"

        if not device.is_active:
            return False, "Device is inactive"

        if device.organization_id != personnel.organization_id:
            return False, "Device does not belong to the personnel organization"

    return True, "Basic eligibility checks passed"