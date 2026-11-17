
import hashlib
import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_personnel, require_roles
from app.database.connections import get_db

from app.models.devices import Device
from app.models.evidence_tags import EvidenceTag
from app.models.evidence import Evidence
from app.models.cases import Case
from app.models.audit_logs import AuditLog

from app.schemas.device import (
    DeviceCreate,
    DeviceResponse,
    DeviceProvisionResponse,
    DeviceKeyRotationResponse,
    DeviceScanRequest,
    DeviceScanResponse,
)


router = APIRouter(
    prefix="/api/devices",
    tags=["Devices"],
)


# ---------------------------------------------------------
# DEVICE KEY FUNCTIONS
# ---------------------------------------------------------

def hash_device_key(api_key: str) -> str:
    """Convert the device API key into a SHA-256 hash."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_device_key() -> str:
    """Generate a secure random API key for a hardware device."""
    return secrets.token_urlsafe(48)


# ---------------------------------------------------------
# DEVICE AUTHENTICATION
# ---------------------------------------------------------

def get_authenticated_device(
    x_device_key: str = Header(..., alias="X-Device-Key"),
    db: Session = Depends(get_db),
) -> Device:
    """
    Authenticate an ESP32 or reader device using its API key.
    Only the hash of the key is stored in PostgreSQL.
    """

    key_hash = hash_device_key(x_device_key)

    device = db.scalar(
        select(Device).where(
            Device.api_key_hash == key_hash
        )
    )

    if device is None or not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive device credentials.",
        )

    return device


# ---------------------------------------------------------
# REGISTER A NEW DEVICE
# ---------------------------------------------------------

@router.post(
    "",
    response_model=DeviceProvisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    current_personnel=Depends(get_current_personnel),
    _role=Depends(require_roles("admin")),
):
    """
    Register a new hardware device.
    Only administrators can register devices.
    """

    # Prevent registration in another organization.
    if payload.organization_id != current_personnel.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot register a device for another organization.",
        )

    # Generate a unique API key.
    api_key = generate_device_key()

    device = Device(
        **payload.model_dump(),
        api_key_hash=hash_device_key(api_key),
    )

    db.add(device)

    try:
        db.flush()

        # Record the registration in the audit log.
        db.add(
            AuditLog(
                personnel_id=current_personnel.id,
                action="DEVICE_REGISTERED",
                resource_type="device",
                resource_id=device.id,
                outcome="success",
                details=f"Registered device {device.device_code}",
            )
        )

        db.commit()
        db.refresh(device)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device code or API key already exists.",
        ) from exc

    # The original API key is returned only once.
    return DeviceProvisionResponse(
        **DeviceResponse.model_validate(device).model_dump(),
        api_key=api_key,
    )


# ---------------------------------------------------------
# LIST REGISTERED DEVICES
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[DeviceResponse],
)
def list_devices(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_personnel=Depends(get_current_personnel),
    _role=Depends(require_roles("admin", "reviewer")),
):
    """
    List devices belonging to the logged-in user's organization.
    """

    query = select(Device).where(
        Device.organization_id == current_personnel.organization_id
    )

    if active_only:
        query = query.where(
            Device.is_active.is_(True)
        )

    query = query.order_by(
        Device.created_at.desc()
    )

    return list(db.scalars(query).all())


# ---------------------------------------------------------
# ROTATE DEVICE API KEY
# ---------------------------------------------------------

@router.patch(
    "/{device_id}/rotate-key",
    response_model=DeviceKeyRotationResponse,
)
def rotate_device_key(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_personnel=Depends(get_current_personnel),
    _role=Depends(require_roles("admin")),
):
    """
    Generate a new API key for a device.
    The previous API key becomes invalid.
    """

    device = db.scalar(
        select(Device).where(
            Device.id == device_id,
            Device.organization_id == current_personnel.organization_id,
        )
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Activate the device before rotating its key.",
        )

    # Generate a replacement key.
    api_key = generate_device_key()

    device.api_key_hash = hash_device_key(api_key)

    db.add(
        AuditLog(
            personnel_id=current_personnel.id,
            action="DEVICE_KEY_ROTATED",
            resource_type="device",
            resource_id=device.id,
            outcome="success",
            details=f"API key rotated for {device.device_code}",
        )
    )

    db.commit()

    return DeviceKeyRotationResponse(
        device_id=device.id,
        device_code=device.device_code,
        api_key=api_key,
        message="Store this key securely. It will not be shown again.",
    )


# ---------------------------------------------------------
# RECEIVE RFID / NFC SCAN FROM HARDWARE
# ---------------------------------------------------------

@router.post(
    "/scan",
    response_model=DeviceScanResponse,
)
def receive_hardware_scan(
    payload: DeviceScanRequest,
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db),
):
    """
    Receive an RFID/NFC tag scan from an authenticated device.
    Validate the tag and identify the linked evidence.
    """

    # Only supported hardware can submit scans.
    if device.device_type not in {
        "ESP32_CONTROLLER",
        "RFID_READER",
        "NFC_READER",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This device type cannot submit tag scans.",
        )

    # Ensure the scan type matches the reader type.
    if (
        device.device_type == "RFID_READER"
        and payload.scan_type != "RFID"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scan type does not match device type.",
        )

    if (
        device.device_type == "NFC_READER"
        and payload.scan_type != "NFC"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scan type does not match device type.",
        )

    device.last_seen_at = datetime.now(timezone.utc)

    # Find the registered active tag.
    # Keep the identifier unchanged during lookup.
    tag = db.scalar(
        select(EvidenceTag).where(
            EvidenceTag.tag_identifier == payload.tag_identifier.strip(),
            EvidenceTag.tag_type == payload.scan_type,
            EvidenceTag.is_active.is_(True),
        )
    )

    # Handle unknown or inactive tags.
    if tag is None:
        db.add(
            AuditLog(
                action="HARDWARE_TAG_SCAN",
                resource_type="evidence_tag",
                outcome="denied",
                details=(
                    f"Unknown or inactive tag scanned by device "
                    f"{device.device_code}"
                ),
            )
        )

        db.commit()

        return DeviceScanResponse(
            success=False,
            message="Tag is not registered or is inactive.",
        )

    # Find the evidence and verify its organization.
    evidence = db.scalar(
        select(Evidence)
        .join(
            Case,
            Evidence.case_id == Case.id,
        )
        .where(
            Evidence.id == tag.evidence_id,
            Case.organization_id == device.organization_id,
        )
    )

    # Prevent cross-organization evidence access.
    if evidence is None:
        db.add(
            AuditLog(
                action="HARDWARE_TAG_SCAN",
                resource_type="evidence_tag",
                resource_id=tag.id,
                outcome="denied",
                details=(
                    f"Tag does not belong to device organization "
                    f"{device.organization_id}"
                ),
            )
        )

        db.commit()

        return DeviceScanResponse(
            success=False,
            message="Tag is not associated with evidence in this organization.",
        )

    # Record a successful scan.
    db.add(
        AuditLog(
            action="HARDWARE_TAG_SCAN",
            resource_type="evidence_tag",
            resource_id=tag.id,
            outcome="success",
            details=(
                f"{payload.scan_type} scan accepted by "
                f"{device.device_code}; "
                f"evidence code {evidence.evidence_code}"
            ),
        )
    )

    db.commit()

    return DeviceScanResponse(
        success=True,
        message="Tag recognized successfully.",
        evidence_id=evidence.id,
        evidence_code=evidence.evidence_code,
        item_name=evidence.item_name,
    )
