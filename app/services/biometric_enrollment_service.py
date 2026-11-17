
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.biometric_enrollments import BiometricEnrollment
from app.models.devices import Device
from app.models.personnel import Personnel
from app.services.audit_service import record_audit_event


def create_enrollment(
    db: Session,
    personnel_id: UUID,
    device_id: UUID,
    template_reference: str,
    actor: Personnel,
) -> BiometricEnrollment:
    person = db.get(Personnel, personnel_id)
    device = db.get(Device, device_id)

    if person is None or person.organization_id != actor.organization_id:
        raise HTTPException(
            status_code=404,
            detail="Personnel was not found in your organisation.",
        )

    if device is None or device.organization_id != actor.organization_id:
        raise HTTPException(
            status_code=404,
            detail="Device was not found in your organisation.",
        )

    if not person.is_active or not device.is_active:
        raise HTTPException(
            status_code=409,
            detail="Personnel and device must both be active.",
        )

    if device.device_type not in {
        "FINGERPRINT_SENSOR",
        "ESP32_CONTROLLER",
    }:
        raise HTTPException(
            status_code=422,
            detail="The selected device is not a fingerprint-capable device.",
        )

    reference = template_reference.strip()

    if not reference:
        raise HTTPException(
            status_code=422,
            detail="Template reference cannot be empty.",
        )

    existing = db.scalar(
        select(BiometricEnrollment).where(
            BiometricEnrollment.device_id == device_id,
            BiometricEnrollment.template_reference == reference,
            BiometricEnrollment.enrollment_status == "active",
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="This sensor template reference is already enrolled.",
        )

    enrollment = BiometricEnrollment(
        personnel_id=personnel_id,
        device_id=device_id,
        template_reference=reference,
        enrollment_status="active",
    )

    db.add(enrollment)
    db.flush()

    record_audit_event(
        db=db,
        action="BIOMETRIC_ENROLLMENT_REFERENCE_CREATED",
        resource_type="biometric_enrollment",
        resource_id=enrollment.id,
        personnel_id=actor.id,
        outcome="success",
        details=(
            f"Template reference {reference} registered "
            f"for personnel {personnel_id} on device {device_id}. "
            "This records a reference only; it does not confirm "
            "physical sensor enrolment."
        ),
    )

    db.commit()
    db.refresh(enrollment)

    return enrollment


def list_enrollments(
    db: Session,
    actor: Personnel,
) -> list[BiometricEnrollment]:
    query = (
        select(BiometricEnrollment)
        .join(
            Personnel,
            BiometricEnrollment.personnel_id == Personnel.id,
        )
        .where(
            Personnel.organization_id == actor.organization_id
        )
        .order_by(BiometricEnrollment.enrolled_at.desc())
    )

    return list(db.scalars(query).all())


def revoke_enrollment(
    db: Session,
    enrollment_id: UUID,
    actor: Personnel,
) -> BiometricEnrollment:
    enrollment = db.get(BiometricEnrollment, enrollment_id)

    if enrollment is None:
        raise HTTPException(
            status_code=404,
            detail="Biometric enrollment was not found.",
        )

    person = db.get(Personnel, enrollment.personnel_id)

    if person is None or person.organization_id != actor.organization_id:
        raise HTTPException(
            status_code=404,
            detail="Biometric enrollment was not found.",
        )

    if enrollment.enrollment_status == "revoked":
        raise HTTPException(
            status_code=409,
            detail="This enrollment has already been revoked.",
        )

    enrollment.enrollment_status = "revoked"
    enrollment.revoked_at = datetime.now(timezone.utc)

    record_audit_event(
        db=db,
        action="BIOMETRIC_ENROLLMENT_REVOKED",
        resource_type="biometric_enrollment",
        resource_id=enrollment.id,
        personnel_id=actor.id,
        outcome="success",
        details=(
            f"Biometric enrollment reference "
            f"{enrollment.template_reference} was revoked."
        ),
    )

    db.commit()
    db.refresh(enrollment)

    return enrollment
