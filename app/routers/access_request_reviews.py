from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_roles
from app.database.connections import get_db
from app.models.personnel import Personnel
from app.schemas.access_request_review import AccessRequestReview
from app.services.access_request_service import decide_access_request


router = APIRouter(
    prefix="/api/access-requests",
    tags=["Access Request Reviews"],
)


@router.post("/{request_id}/review")
def review_access_request(
    request_id: UUID,
    payload: AccessRequestReview,
    current_personnel: Personnel = Depends(
        require_roles("admin", "reviewer")
    ),
    db: Session = Depends(get_db),
):
    try:
        request = decide_access_request(
            db=db,
            request_id=request_id,
            reviewer_personnel_id=current_personnel.id,
            decision=payload.decision,
            decision_reason=payload.decision_reason,
        )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to process the access-request review.",
        )

    return {
        "id": str(request.id),
        "status": request.status,
        "reviewed_by_personnel_id": (
            str(request.reviewed_by_personnel_id)
            if request.reviewed_by_personnel_id
            else None
        ),
        "decision_reason": request.decision_reason,
        "decided_at": request.decided_at,
    }