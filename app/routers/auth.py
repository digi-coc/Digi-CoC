from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.core.security import (
    ACCESS_TOKEN_MINUTES,
    create_access_token,
    verify_password,
)
from app.database.connections import get_db
from app.models.organisations import Organization
from app.models.personnel import Personnel
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.auth import get_current_personnel


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    organization_code = payload.organization_code.strip()
    personnel_code = payload.personnel_code.strip()

    organization = db.scalar(
        select(Organization).where(
            Organization.organization_code == organization_code
        )
    )

    # Use the same external error for invalid credentials to avoid
    # revealing whether a particular account exists.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid organization code, personnel code, or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if organization is None:
        raise invalid_credentials

    personnel = db.scalar(
        select(Personnel).where(
            Personnel.organization_id == organization.id,
            Personnel.personnel_code == personnel_code,
        )
    )

    if (
        personnel is None
        or not personnel.is_active
        or not personnel.password_hash
    ):
        raise invalid_credentials

    if not verify_password(payload.password, personnel.password_hash):
        raise invalid_credentials

    token = create_access_token(personnel.id)

    return LoginResponse(
        access_token=token,
        expires_in=ACCESS_TOKEN_MINUTES * 60,
        personnel_id=str(personnel.id),
        personnel_code=personnel.personnel_code,
        full_name=personnel.full_name,
        role=personnel.role,
    )
@router.get("/me")
def get_my_profile(
    current_personnel: Personnel = Depends(get_current_personnel),
):
    return {
        "personnel_id": str(current_personnel.id),
        "personnel_code": current_personnel.personnel_code,
        "full_name": current_personnel.full_name,
        "role": current_personnel.role,
        "organization_id": str(current_personnel.organization_id),
        "is_active": current_personnel.is_active,
    }