
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.database.connections import get_db
from app.models.personnel import Personnel

from app.schemas.biometric_enrollment import (
    BiometricEnrollmentResponse,
)
from app.schemas.biometric_enrollment_session import (
    BiometricEnrollmentSessionCreate,
    BiometricEnrollmentSessionResponse,
    BiometricEnrollmentSessionProvisionResponse,
    BiometricEnrollmentSessionCancelResponse,
)

from app.services.biometric_enrollment_service import (
    list_enrollments,
    revoke_enrollment,
)

from app.services.biometric_enrollment_session_service import (
    create_enrollment_session,
    get_enrollment_session,
    cancel_enrollment_session,
)


router = APIRouter(
    prefix="/api/biometric-enrollments",
    tags=["Biometric Enrollments"],
)


@router.get(
    "",
    response_model=list[BiometricEnrollmentResponse],
)
def get_enrollments(
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
):
    return list_enrollments(
        db=db,
        actor=current_personnel,
    )


@router.patch(
    "/{enrollment_id}/revoke",
    response_model=BiometricEnrollmentResponse,
)
def revoke_biometric_enrollment(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin")
    ),
):
    return revoke_enrollment(
        db=db,
        enrollment_id=enrollment_id,
        actor=current_personnel,
    )


@router.post(
    "/sessions",
    response_model=BiometricEnrollmentSessionProvisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_biometric_session(
    payload: BiometricEnrollmentSessionCreate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin")
    ),
):
    session, token = create_enrollment_session(
        db=db,
        admin=current_personnel,
        personnel_id=payload.personnel_id,
        device_id=payload.device_id,
        finger_position=payload.finger_position,
    )

    session_data = BiometricEnrollmentSessionResponse.model_validate(
        session
    ).model_dump()

    return BiometricEnrollmentSessionProvisionResponse(
        **session_data,
        session_token=token,
        message=(
            "Enrollment session created. The token is shown only once. "
            "Deliver it securely to the assigned ESP32 controller."
        ),
    )


@router.get(
    "/sessions/{session_id}",
    response_model=BiometricEnrollmentSessionResponse,
)
def read_biometric_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
):
    return get_enrollment_session(
        db=db,
        session_id=session_id,
        admin=current_personnel,
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=BiometricEnrollmentSessionCancelResponse,
)
def cancel_biometric_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(
        require_roles("admin")
    ),
):
    session = cancel_enrollment_session(
        db=db,
        session_id=session_id,
        admin=current_personnel,
    )

    return BiometricEnrollmentSessionCancelResponse(
        success=True,
        session_id=session.id,
        message="Enrollment session cancelled.",
    )
