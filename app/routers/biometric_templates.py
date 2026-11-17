import base64

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.database.connections import get_db

from app.models.devices import Device
from app.models.personnel import Personnel

from app.routers.devices import get_authenticated_device

from app.schemas.biometric_template import (
    BiometricTemplateEnroll,
    BiometricTemplateEnrollResponse,
    BiometricTemplateMetadataResponse,
    BiometricTemplateDeviceResponse,
)

from app.services.biometric_template_service import (
    enroll_fingerprint_template,
    list_template_metadata,
    get_template_for_device,
    revoke_fingerprint_template,
)


router = APIRouter(
    prefix="/api/biometric-templates",
    tags=["Biometric Templates"],
)


# ---------------------------------------------------------
# ADMIN / REVIEWER: LIST TEMPLATE METADATA
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[BiometricTemplateMetadataResponse],
)
def get_biometric_templates(
    db: Session = Depends(get_db),
    admin: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
):
    return list_template_metadata(
        db=db,
        admin=admin,
    )


# ---------------------------------------------------------
# ADMIN: REVOKE A FINGERPRINT TEMPLATE
# ---------------------------------------------------------

@router.patch(
    "/{fingerprint_id}/revoke",
    response_model=BiometricTemplateMetadataResponse,
)
def revoke_biometric_template(
    fingerprint_id: int,
    db: Session = Depends(get_db),
    admin: Personnel = Depends(
        require_roles("admin")
    ),
):
    return revoke_fingerprint_template(
        db=db,
        fingerprint_id=fingerprint_id,
        admin=admin,
    )


# ---------------------------------------------------------
# DEVICE: UPLOAD A FINGERPRINT TEMPLATE
# ---------------------------------------------------------

@router.post(
    "/device/enroll",
    response_model=BiometricTemplateEnrollResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_fingerprint_template(
    payload: BiometricTemplateEnroll,
    x_enrollment_token: str = Header(
        ...,
        alias="X-Enrollment-Token",
    ),
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db),
):
    try:
        template = enroll_fingerprint_template(
            db=db,
            device=device,
            session_token=x_enrollment_token,
            payload=payload,
        )

        return BiometricTemplateEnrollResponse(
            success=True,
            fingerprint_id=template.fingerprint_id,
            personnel_id=template.personnel_id,
            finger_position=template.finger_position,
            message=(
                "Fingerprint template encrypted and enrolled successfully."
            ),
        )

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Fingerprint enrollment conflicts with an existing record."
            ),
        ) from exc


# ---------------------------------------------------------
# DEVICE: RETRIEVE AN AUTHORISED FINGERPRINT TEMPLATE
# ---------------------------------------------------------

@router.get(
    "/device/{fingerprint_id}",
    response_model=BiometricTemplateDeviceResponse,
)
def download_fingerprint_template(
    fingerprint_id: int,
    device: Device = Depends(get_authenticated_device),
    db: Session = Depends(get_db),
):
    template, decrypted_template = get_template_for_device(
        db=db,
        device=device,
        fingerprint_id=fingerprint_id,
    )

    return BiometricTemplateDeviceResponse(
        fingerprint_id=template.fingerprint_id,
        personnel_id=template.personnel_id,
        template_format=template.template_format,
        template_data=base64.b64encode(
            decrypted_template
        ).decode("ascii"),
        template_checksum=template.template_checksum,
    )