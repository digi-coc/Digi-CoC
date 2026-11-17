from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database_old import get_db
from app.models.organisations import Organization
from app.models.personnel import Personnel
from app.schemas.personnel import (
    PersonnelCreate,
    PersonnelResponse,
    PersonnelUpdate,
)


router = APIRouter(
    prefix="/api/personnel",
    tags=["Personnel"],
)


@router.post(
    "",
    response_model=PersonnelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_personnel(
    payload: PersonnelCreate,
    db: Session = Depends(get_db),
):
    organization = db.get(Organization, payload.organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization was not found.",
        )

    person = Personnel(**payload.model_dump())
    db.add(person)

    try:
        db.commit()
        db.refresh(person)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Personnel record could not be created.",
        ) from exc

    return person


@router.get("", response_model=list[PersonnelResponse])
def list_personnel(
    organization_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Personnel)

    if organization_id is not None:
        query = query.where(
            Personnel.organization_id == organization_id
        )

    query = (
        query.order_by(Personnel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


@router.get("/{personnel_id}", response_model=PersonnelResponse)
def get_personnel(
    personnel_id: UUID,
    db: Session = Depends(get_db),
):
    person = db.get(Personnel, personnel_id)

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Personnel record was not found.",
        )

    return person


@router.patch("/{personnel_id}", response_model=PersonnelResponse)
def update_personnel(
    personnel_id: UUID,
    payload: PersonnelUpdate,
    db: Session = Depends(get_db),
):
    person = db.get(Personnel, personnel_id)

    if person is None:
        raise HTTPException(
            status_code=404,
            detail="Personnel record was not found.",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(person, field, value)

    try:
        db.commit()
        db.refresh(person)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Personnel record could not be updated.",
        ) from exc

    return person