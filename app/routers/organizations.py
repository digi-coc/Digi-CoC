
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connections import get_db
from app.models.organisations import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)

router = APIRouter(
    prefix="/api/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(Organization).where(
            Organization.organization_code == payload.organization_code
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization code already exists",
        )

    organization = Organization(**payload.model_dump())

    try:
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization could not be created due to a data conflict",
        )


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
):
    statement = select(Organization).order_by(Organization.created_at.desc())
    return list(db.scalars(statement).all())
