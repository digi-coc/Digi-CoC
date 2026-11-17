from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database_old import get_db
from app.models.cases import Case
from app.models.organisations import Organization
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"],
)


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
):
    # Verify that the organization exists.
    organization = (
        db.query(Organization)
        .filter(Organization.id == case_data.organization_id)
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found.",
        )

    # Prevent duplicate case codes within the same organization.
    existing_case = (
        db.query(Case)
        .filter(
            Case.organization_id == case_data.organization_id,
            Case.case_code == case_data.case_code,
        )
        .first()
    )

    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This case code already exists for this organization.",
        )

    new_case = Case(**case_data.model_dump())
    db.add(new_case)

    try:
        db.commit()
        db.refresh(new_case)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create the case.",
        )

    return new_case


@router.get("", response_model=list[CaseResponse])
def list_cases(db: Session = Depends(get_db)):
    return db.query(Case).order_by(Case.case_code).all()
