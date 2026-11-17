from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connections import get_db
from app.models.access_requests import AccessRequest
from app.models.devices import Device
from app.models.evidence import Evidence
from app.models.personnel import Personnel
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
)
from app.services.authorization import evaluate_access_request
from app.services.audit_service import record_audit_event
from app.services.security_service import record_unauthorized_attempt

router = APIRouter(
    prefix="/api/access-requests",
    tags=["Access Requests"],
)


@router.post(
    "",
    response_model=AccessRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_access_request(
    payload: AccessRequestCreate,
    db: Session = Depends(get_db),
):
    evidence = db.get(Evidence, payload.evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence record not found",
        )

    personnel = db.get(Personnel, payload.personnel_id)

    if personnel is None:
        raise HTTPException(
            status_code=404,
            detail="Personnel record not found",
        )

    if payload.device_id is not None:
        device = db.get(Device, payload.device_id)

        if device is None:
            raise HTTPException(
                status_code=404,
                detail="Device record not found",
            )

    eligible, reason = evaluate_access_request(
        db=db,
        evidence_id=payload.evidence_id,
        personnel_id=payload.personnel_id,
        device_id=payload.device_id,
    )

    request_record = AccessRequest(
        evidence_id=payload.evidence_id,
        personnel_id=payload.personnel_id,
        device_id=payload.device_id,
        request_reason=payload.request_reason,
        correlation_id=payload.correlation_id,
        status="pending",
    )

    db.add(request_record)

    try:
        if not eligible:
            record_unauthorized_attempt(
                db=db,
                evidence_id=payload.evidence_id,
                personnel_id=payload.personnel_id,
                attempt_type="ACCESS_REQUEST",
                reason=reason,
            )

        record_audit_event(
            db=db,
            action="ACCESS_REQUEST_CREATED",
            resource_type="evidence",
            resource_id=payload.evidence_id,
            personnel_id=payload.personnel_id,
            outcome="submitted",
            details=(
                f"Request created. Eligibility: {reason}"
            ),
            correlation_id=payload.correlation_id,
        )

        db.commit()
        db.refresh(request_record)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The access request could not be saved because of a database constraint",
        )

    return request_record


@router.get(
    "",
    response_model=list[AccessRequestResponse],
)
def list_access_requests(
    request_status: str | None = Query(default=None, alias="status"),
    evidence_id: UUID | None = None,
    personnel_id: UUID | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(AccessRequest)

    if request_status is not None:
        query = query.where(AccessRequest.status == request_status)

    if evidence_id is not None:
        query = query.where(AccessRequest.evidence_id == evidence_id)

    if personnel_id is not None:
        query = query.where(AccessRequest.personnel_id == personnel_id)

    query = (
        query.order_by(AccessRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


@router.get(
    "/{request_id}",
    response_model=AccessRequestResponse,
)
def get_access_request(
    request_id: UUID,
    db: Session = Depends(get_db),
):
    request_record = db.get(AccessRequest, request_id)

    if request_record is None:
        raise HTTPException(
            status_code=404,
            detail="Access request not found",
        )

    return request_record