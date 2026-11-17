import base64
import hashlib
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.biometric_templates import BiometricTemplate
from app.models.biometric_enrollment_sessions import (
    BiometricEnrollmentSession,
)
from app.models.biometric_enrollments import BiometricEnrollment
from app.models.devices import Device
from app.models.personnel import Personnel

from app.services.biometric_encryption_service import (
    encrypt_template,
    decrypt_template,
    get_encryption_key_version,
    calculate_template_checksum,
    verify_template_checksum,
)

from app.services.audit_service import record_audit_event


def _hash_session_token(token: str) -> str:
    """Hash the one-time enrollment token before searching for it."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def _audit(
    db: Session,
    action: str,
    outcome: str,
    personnel_id=None,
    resource_id=None,
    details: str | None = None,
):
    """Add an audit record to the current transaction."""

    record_audit_event(
        db=db,
        action=action,
        resource_type="BIOMETRIC_TEMPLATE",
        outcome=outcome,
        personnel_id=personnel_id,
        resource_id=resource_id,
        details=details,
    )


def enroll_fingerprint_template(
    db: Session,
    device: Device,
    session_token: str,
    payload,
) -> BiometricTemplate:
    """
    Validate the enrollment session and securely store a fingerprint.

    The session determines the personnel, organization, and finger.
    The device cannot override those values in its upload request.
    """

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Enrollment session token is required.",
        )

    token_hash = _hash_session_token(session_token)

    enrollment_session = db.scalar(
        select(BiometricEnrollmentSession)
        .where(
            BiometricEnrollmentSession.session_token_hash
            == token_hash
        )
        .with_for_update()
    )

    if enrollment_session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid enrollment session token.",
        )

    now = datetime.now(timezone.utc)

    if enrollment_session.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Enrollment session is no longer pending.",
        )

    if enrollment_session.expires_at <= now:
        enrollment_session.status = "expired"
        db.commit()

        raise HTTPException(
            status_code=410,
            detail="Enrollment session has expired.",
        )

    if enrollment_session.device_id != device.id:
        raise HTTPException(
            status_code=403,
            detail="Enrollment session belongs to another device.",
        )

    if enrollment_session.organization_id != device.organization_id:
        raise HTTPException(
            status_code=403,
            detail="Device and enrollment session organizations do not match.",
        )

    if device.device_type != "ESP32_CONTROLLER":
        raise HTTPException(
            status_code=403,
            detail="This device cannot upload fingerprint templates.",
        )

    # The enrollment session is the authoritative source.
    personnel = db.get(
        Personnel,
        enrollment_session.personnel_id,
    )

    if (
        personnel is None
        or not personnel.is_active
        or personnel.organization_id != device.organization_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Active personnel record was not found.",
        )

    # Decode the Base64 template supplied by the device.
    try:
        template_bytes = base64.b64decode(
            payload.template_data,
            validate=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail="Fingerprint template is not valid Base64.",
        ) from exc

    if not template_bytes:
        raise HTTPException(
            status_code=422,
            detail="Fingerprint template cannot be empty.",
        )

    # Verify the checksum before encryption.
    actual_checksum = calculate_template_checksum(
        template_bytes
    )

    if not verify_template_checksum(
        template_bytes,
        payload.template_checksum,
    ):
        raise HTTPException(
            status_code=422,
            detail="Fingerprint template checksum does not match.",
        )

    # Prevent duplicate active enrollment for the same finger.
    existing_template = db.scalar(
        select(BiometricTemplate).where(
            BiometricTemplate.personnel_id == personnel.id,
            BiometricTemplate.finger_position
            == enrollment_session.finger_position,
            BiometricTemplate.is_active.is_(True),
        )
    )

    if existing_template is not None:
        raise HTTPException(
            status_code=409,
            detail="This finger already has an active biometric template.",
        )

    # Encrypt the template before saving it.
    encrypted_template = encrypt_template(
        template_bytes
    )

    template = BiometricTemplate(
        personnel_id=personnel.id,
        organization_id=device.organization_id,
        finger_position=enrollment_session.finger_position,
        sensor_model=payload.sensor_model,
        template_format=payload.template_format,
        template_data=encrypted_template,
        template_checksum=actual_checksum,
        encryption_key_version=get_encryption_key_version(),
        is_active=True,
        created_by=enrollment_session.created_by,
    )

    try:
        db.add(template)

        # Flush generates the database fingerprint ID.
        db.flush()

        # Link the new template to the authorised device.
        enrollment = BiometricEnrollment(
            personnel_id=personnel.id,
            device_id=device.id,
            template_reference=str(template.fingerprint_id),
            enrollment_status="active",
        )

        db.add(enrollment)

        # Mark the one-time enrollment session as completed.
        enrollment_session.status = "completed"
        enrollment_session.completed_at = now

        device.last_seen_at = now

        _audit(
            db=db,
            action="BIOMETRIC_TEMPLATE_ENROLLED",
            outcome="success",
            personnel_id=enrollment_session.created_by,
            resource_id=template.id,
            details=(
                f"Fingerprint template {template.fingerprint_id} "
                f"enrolled for personnel {personnel.id}; "
                f"finger position: "
                f"{enrollment_session.finger_position}; "
                f"device: {device.id}."
            ),
        )

        db.commit()
        db.refresh(template)

        return template

    except IntegrityError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


def list_template_metadata(
    db: Session,
    admin: Personnel,
) -> list[BiometricTemplate]:
    """List biometric template metadata for one organization."""

    query = (
        select(BiometricTemplate)
        .where(
            BiometricTemplate.organization_id
            == admin.organization_id
        )
        .order_by(
            BiometricTemplate.created_at.desc()
        )
    )

    return list(db.scalars(query).all())


def get_template_for_device(
    db: Session,
    device: Device,
    fingerprint_id: int,
) -> tuple[BiometricTemplate, bytes]:
    """
    Return a decrypted template only to a device with an active
    enrollment reference for that template.
    """

    template = db.scalar(
        select(BiometricTemplate).where(
            BiometricTemplate.fingerprint_id == fingerprint_id,
            BiometricTemplate.organization_id
            == device.organization_id,
            BiometricTemplate.is_active.is_(True),
        )
    )

    if template is None:
        raise HTTPException(
            status_code=404,
            detail="Active fingerprint template was not found.",
        )

    enrollment = db.scalar(
        select(BiometricEnrollment).where(
            BiometricEnrollment.personnel_id
            == template.personnel_id,
            BiometricEnrollment.device_id == device.id,
            BiometricEnrollment.template_reference
            == str(fingerprint_id),
            BiometricEnrollment.enrollment_status == "active",
        )
    )

    if enrollment is None:
        raise HTTPException(
            status_code=403,
            detail="This device is not authorised to retrieve this template.",
        )

    try:
        decrypted_template = decrypt_template(
            template.template_data
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Fingerprint template could not be decrypted.",
        ) from exc

    if not verify_template_checksum(
        decrypted_template,
        template.template_checksum,
    ):
        raise HTTPException(
            status_code=500,
            detail="Fingerprint template integrity verification failed.",
        )

    device.last_seen_at = datetime.now(timezone.utc)
    db.commit()

    return template, decrypted_template


def revoke_fingerprint_template(
    db: Session,
    fingerprint_id: int,
    admin: Personnel,
) -> BiometricTemplate:
    """Revoke a template and all active device references to it."""

    template = db.scalar(
        select(BiometricTemplate)
        .where(
            BiometricTemplate.fingerprint_id == fingerprint_id,
            BiometricTemplate.organization_id
            == admin.organization_id,
        )
        .with_for_update()
    )

    if template is None:
        raise HTTPException(
            status_code=404,
            detail="Fingerprint template was not found.",
        )

    if not template.is_active:
        raise HTTPException(
            status_code=409,
            detail="Fingerprint template has already been revoked.",
        )

    now = datetime.now(timezone.utc)

    template.is_active = False
    template.revoked_at = now

    references = db.scalars(
        select(BiometricEnrollment).where(
            BiometricEnrollment.personnel_id
            == template.personnel_id,
            BiometricEnrollment.template_reference
            == str(fingerprint_id),
            BiometricEnrollment.enrollment_status == "active",
        )
    ).all()

    for reference in references:
        reference.enrollment_status = "revoked"
        reference.revoked_at = now

    _audit(
        db=db,
        action="BIOMETRIC_TEMPLATE_REVOKED",
        outcome="success",
        personnel_id=admin.id,
        resource_id=template.id,
        details=(
            f"Fingerprint template {fingerprint_id} and "
            f"{len(references)} active device reference(s) revoked."
        ),
    )

    db.commit()
    db.refresh(template)

    return template