
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.database.connections import get_db

from app.models.biometric_verifications import BiometricVerification
from app.models.biometric_templates import BiometricTemplate
from app.models.biometric_enrollments import BiometricEnrollment
from app.models.devices import Device
from app.models.personnel import Personnel

from app.schemas.biometric_verification import (
    BiometricDeviceVerificationCreate,
    BiometricVerificationResponse,
)

from app.routers.devices import get_authenticated_device
from app.services.audit_service import record_audit_event


router = APIRouter(
    prefix="/api/biometric-verifications",
    tags=["Biometric Verifications"],
)


# ---------------------------------------------------------
# HARDWARE: SUBMIT A FINGERPRINT VERIFICATION RESULT
# ---------------------------------------------------------

@router.post(
    "/device",
    response_model=BiometricVerificationResponse,
)
def submit_device_verification(
    payload: BiometricDeviceVerificationCreate,
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db),
):
    if device.device_type != "ESP32_CONTROLLER":
        raise HTTPException(
            status_code=403,
            detail="This device cannot submit biometric verification results.",
        )

    personnel_id = None

    if payload.result == "success":
        if payload.fingerprint_id is None:
            raise HTTPException(
                status_code=422,
                detail="Fingerprint ID is required for a successful verification.",
            )

        template = db.scalar(
            select(BiometricTemplate).where(
                BiometricTemplate.fingerprint_id == payload.fingerprint_id,
                BiometricTemplate.organization_id == device.organization_id,
                BiometricTemplate.is_active.is_(True),
            )
        )

        if template is None:
            raise HTTPException(
                status_code=403,
                detail="No active fingerprint template exists for this device organization.",
            )

        enrollment = db.scalar(
            select(BiometricEnrollment).where(
                BiometricEnrollment.personnel_id == template.personnel_id,
                BiometricEnrollment.device_id == device.id,
                BiometricEnrollment.template_reference == str(
                    payload.fingerprint_id
                ),
                BiometricEnrollment.enrollment_status == "active",
            )
        )

        if enrollment is None:
            raise HTTPException(
                status_code=403,
                detail="This device is not authorized to verify this fingerprint.",
            )

        personnel = db.get(Personnel, template.personnel_id)

        if personnel is None or not personnel.is_active:
            raise HTTPException(
                status_code=403,
                detail="Personnel account is inactive.",
            )

        personnel_id = personnel.id

    verification = BiometricVerification(
        personnel_id=personnel_id,
        device_id=device.id,
        verification_method="fingerprint_sensor",
        result=payload.result,
        correlation_id=payload.correlation_id,
    )

    db.add(verification)

    device.last_seen_at = __import__(
        "datetime"
    ).datetime.now(
        __import__("datetime").timezone.utc
    )

    record_audit_event(
        db=db,
        action="BIOMETRIC_VERIFICATION",
        resource_type="BIOMETRIC_VERIFICATION",
        resource_id=verification.id,
        personnel_id=personnel_id,
        outcome=payload.result,
        details=(
            f"Biometric verification result reported by device "
            f"{device.device_code}."
        ),
        correlation_id=payload.correlation_id,
    )

    db.commit()
    db.refresh(verification)

    return verification


# ---------------------------------------------------------
# ADMIN / REVIEWER: LIST VERIFICATION RECORDS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[BiometricVerificationResponse],
)
def list_biometric_verifications(
    personnel_id: UUID | None = Query(default=None),
    correlation_id: str | None = Query(
        default=None,
        max_length=100,
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
    db: Session = Depends(get_db),
):
    query = (
        select(BiometricVerification)
        .join(
            Device,
            BiometricVerification.device_id == Device.id,
        )
        .where(
            Device.organization_id == current_personnel.organization_id
        )
    )

    if personnel_id is not None:
        query = query.where(
            BiometricVerification.personnel_id == personnel_id
        )

    if correlation_id is not None:
        query = query.where(
            BiometricVerification.correlation_id == correlation_id
        )

    query = (
        query.order_by(
            BiometricVerification.verified_at.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


# ---------------------------------------------------------
# ADMIN / REVIEWER: GET ONE VERIFICATION RECORD
# ---------------------------------------------------------

@router.get(
    "/{verification_id}",
    response_model=BiometricVerificationResponse,
)
def get_biometric_verification(
    verification_id: UUID,
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
    db: Session = Depends(get_db),
):
    verification = db.scalar(
        select(BiometricVerification)
        .join(
            Device,
            BiometricVerification.device_id == Device.id,
        )
        .where(
            BiometricVerification.id == verification_id,
            Device.organization_id == current_personnel.organization_id,
        )
    )

    if verification is None:
        raise HTTPException(
            status_code=404,
            detail="Biometric verification record not found.",
        )

    return verification
