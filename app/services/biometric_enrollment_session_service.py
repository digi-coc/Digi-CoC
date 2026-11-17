
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.biometric_enrollment_sessions import (
    BiometricEnrollmentSession,
)
from app.models.devices import Device
from app.models.personnel import Personnel
from app.services.audit_service import record_audit_event


SESSION_VALIDITY_MINUTES = 5


def create_enrollment_session(
    db: Session,
    admin: Personnel,
    personnel_id: UUID,
    device_id: UUID,
    finger_position: str,
) -> tuple[BiometricEnrollmentSession, str]:
    """
    Create a short-lived, one-time authorization for fingerprint enrollment.

    Returns:
        (enrollment_session, plaintext_session_token)

    Only the token hash is stored in PostgreSQL.
    The plaintext token is returned once to the authorized admin.
    """

    # Only administrators may initiate fingerprint enrollment.
    if (admin.role or "").strip().lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can initiate fingerprint enrollment.",
        )

    # Lock and retrieve the personnel record.
    personnel = db.scalar(
        select(Personnel)
        .where(Personnel.id == personnel_id)
        .with_for_update()
    )

    if personnel is None or not personnel.is_active:
        raise HTTPException(
            status_code=404,
            detail="Active personnel record was not found.",
        )

    # Personnel and administrator must belong to the same organization.
    if personnel.organization_id != admin.organization_id:
        raise HTTPException(
            status_code=403,
            detail="Personnel belongs to another organization.",
        )

    # Retrieve and validate the hardware device.
    device = db.scalar(
        select(Device)
        .where(Device.id == device_id)
        .with_for_update()
    )

    if device is None or not device.is_active:
        raise HTTPException(
            status_code=404,
            detail="Active enrollment device was not found.",
        )

    if device.organization_id != admin.organization_id:
        raise HTTPException(
            status_code=403,
            detail="Device belongs to another organization.",
        )

    if device.device_type != "ESP32_CONTROLLER":
        raise HTTPException(
            status_code=400,
            detail="Selected device is not an ESP32 controller.",
        )

    # Check for an existing unexpired session for this same finger.
    now = datetime.now(timezone.utc)

    existing_session = db.scalar(
        select(BiometricEnrollmentSession)
        .where(
            BiometricEnrollmentSession.personnel_id == personnel.id,
            BiometricEnrollmentSession.finger_position == finger_position,
            BiometricEnrollmentSession.status == "pending",
            BiometricEnrollmentSession.expires_at > now,
        )
        .with_for_update()
    )

    if existing_session is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "An active enrollment session already exists "
                "for this personnel member and finger."
            ),
        )

    # Generate a cryptographically random one-time token.
    session_token = secrets.token_urlsafe(32)

    # Store only the SHA-256 hash of the token.
    session_token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    enrollment_session = BiometricEnrollmentSession(
        personnel_id=personnel.id,
        organization_id=admin.organization_id,
        device_id=device.id,
        created_by=admin.id,
        finger_position=finger_position,
        status="pending",
        session_token_hash=session_token_hash,
        expires_at=now + timedelta(
            minutes=SESSION_VALIDITY_MINUTES
        ),
    )

    try:
        db.add(enrollment_session)
        db.flush()

        # Record the action without logging the token.
        record_audit_event(
            db=db,
            action="BIOMETRIC_ENROLLMENT_SESSION_CREATED",
            resource_type="BIOMETRIC_ENROLLMENT_SESSION",
            resource_id=enrollment_session.id,
            personnel_id=admin.id,
            outcome="SUCCESS",
            details=(
                f"Enrollment initiated for personnel {personnel.id}; "
                f"device {device.id}; "
                f"finger position {finger_position}."
            ),
        )

        db.commit()
        db.refresh(enrollment_session)

    except Exception:
        db.rollback()
        raise

    return enrollment_session, session_token


def get_enrollment_session(
    db: Session,
    session_id: UUID,
    admin: Personnel,
) -> BiometricEnrollmentSession:
    """Retrieve an enrollment session within the admin's organization."""

    enrollment_session = db.scalar(
        select(BiometricEnrollmentSession).where(
            BiometricEnrollmentSession.id == session_id,
            BiometricEnrollmentSession.organization_id
            == admin.organization_id,
        )
    )

    if enrollment_session is None:
        raise HTTPException(
            status_code=404,
            detail="Enrollment session was not found.",
        )

    return enrollment_session


def cancel_enrollment_session(
    db: Session,
    session_id: UUID,
    admin: Personnel,
) -> BiometricEnrollmentSession:
    """Cancel a pending enrollment session."""

    enrollment_session = db.scalar(
        select(BiometricEnrollmentSession)
        .where(
            BiometricEnrollmentSession.id == session_id,
            BiometricEnrollmentSession.organization_id
            == admin.organization_id,
        )
        .with_for_update()
    )

    if enrollment_session is None:
        raise HTTPException(
            status_code=404,
            detail="Enrollment session was not found.",
        )

    if enrollment_session.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Only pending enrollment sessions can be cancelled.",
        )

    enrollment_session.status = "cancelled"

    try:
        record_audit_event(
            db=db,
            action="BIOMETRIC_ENROLLMENT_SESSION_CANCELLED",
            resource_type="BIOMETRIC_ENROLLMENT_SESSION",
            resource_id=enrollment_session.id,
            personnel_id=admin.id,
            outcome="SUCCESS",
            details="Pending biometric enrollment session cancelled.",
        )

        db.commit()
        db.refresh(enrollment_session)

    except Exception:
        db.rollback()
        raise

    return enrollment_session
