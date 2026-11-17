
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_personnel, require_roles
from app.database.connections import get_db

from app.models.access_requests import AccessRequest
from app.models.biometric_verifications import BiometricVerification
from app.models.cases import Case
from app.models.custody_events import CustodyEvent
from app.models.devices import Device
from app.models.evidence import Evidence
from app.models.personnel import Personnel

from app.schemas.custody_event import (
    CustodyEventCreate,
    CustodyEventResponse,
    CustodyIntegrityResponse,
    CustodyCorrectionCreate,
    CustodyCorrectionResponse,
)

from app.services.audit_service import record_audit_event

from app.services.custody_integrity_service import (
    calculate_event_hash,
    verify_event_chain,
    get_chain_tip,
)


router = APIRouter(
    prefix="/api/custody-events",
    tags=["Custody Events"],
)


# ---------------------------------------------------------
# ORGANIZATION VALIDATION
# ---------------------------------------------------------

def _ensure_same_organization(
    personnel: Personnel,
    organization_id: UUID,
):
    """Ensure personnel belongs to the evidence organization."""

    if personnel.organization_id != organization_id:
        raise HTTPException(
            status_code=403,
            detail="Personnel does not belong to the evidence organization.",
        )


# ---------------------------------------------------------
# CREATE CUSTODY TRANSFER
# ---------------------------------------------------------

@router.post(
    "",
    response_model=CustodyEventResponse,
    status_code=201,
)
def create_custody_event(
    payload: CustodyEventCreate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    """
    Record a custody transfer after validating:
    - Evidence and organization
    - Receiving personnel
    - Approved access request
    - Device, if provided
    - Biometric verification or supervised manual verification
    """

    try:
        # Lock the evidence row to prevent simultaneous transfers.
        evidence = db.scalar(
            select(Evidence)
            .where(Evidence.id == payload.evidence_id)
            .with_for_update()
        )

        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail="Evidence was not found.",
            )

        case = db.get(Case, evidence.case_id)

        if case is None:
            raise HTTPException(
                status_code=409,
                detail="Evidence case was not found.",
            )

        _ensure_same_organization(
            current_personnel,
            case.organization_id,
        )

        # Validate receiving personnel.
        recipient = db.get(
            Personnel,
            payload.to_personnel_id,
        )

        if recipient is None or not recipient.is_active:
            raise HTTPException(
                status_code=404,
                detail="Active receiving personnel was not found.",
            )

        _ensure_same_organization(
            recipient,
            case.organization_id,
        )

        if current_personnel.id == recipient.id:
            raise HTTPException(
                status_code=409,
                detail="Sender and recipient must be different.",
            )

        # Validate approved access request.
        access_request = db.get(
            AccessRequest,
            payload.access_request_id,
        )

        if access_request is None:
            raise HTTPException(
                status_code=404,
                detail="Access request was not found.",
            )

        if access_request.status != "approved":
            raise HTTPException(
                status_code=409,
                detail="An approved access request is required.",
            )

        if (
            access_request.evidence_id != evidence.id
            or access_request.personnel_id != recipient.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Access request does not authorize this transfer.",
            )

        if (
            access_request.device_id
            and access_request.device_id != payload.device_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Device does not match the approved request.",
            )

        # Prevent reuse of an access request.
        existing_event = db.scalar(
            select(CustodyEvent).where(
                CustodyEvent.access_request_id == access_request.id
            )
        )

        if existing_event is not None:
            raise HTTPException(
                status_code=409,
                detail="This access request has already been used.",
            )

        # Validate device if supplied.
        if payload.device_id is not None:

            device = db.get(Device, payload.device_id)

            if device is None or not device.is_active:
                raise HTTPException(
                    status_code=404,
                    detail="Active device was not found.",
                )

            _ensure_same_organization(
                device,
                case.organization_id,
            )

        # Validate biometric verification.
        biometric = None

        if payload.biometric_verification_id is not None:

            biometric = db.get(
                BiometricVerification,
                payload.biometric_verification_id,
            )

            if biometric is None:
                raise HTTPException(
                    status_code=404,
                    detail="Biometric verification was not found.",
                )

            if biometric.result != "success":
                raise HTTPException(
                    status_code=403,
                    detail="Successful biometric verification is required.",
                )

            if biometric.personnel_id != recipient.id:
                raise HTTPException(
                    status_code=403,
                    detail="Biometric verification does not match recipient.",
                )

            if (
                payload.device_id
                and biometric.device_id != payload.device_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Biometric device does not match.",
                )

            if (
                access_request.correlation_id
                and biometric.correlation_id
                != access_request.correlation_id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Biometric correlation ID does not match.",
                )

            if (
                payload.verification_method
                and payload.verification_method
                != biometric.verification_method
            ):
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Verification method does not match "
                        "biometric record."
                    ),
                )

            verification_method = biometric.verification_method

        else:

            # Manual verification is restricted to admin/reviewer.
            if payload.verification_method != "manual_supervised":
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Without a biometric record, "
                        "verification_method must be manual_supervised."
                    ),
                )

            actor_role = (
                current_personnel.role or ""
            ).strip().lower()

            if actor_role not in {"admin", "reviewer"}:
                raise HTTPException(
                    status_code=403,
                    detail="Manual transfers require an admin or reviewer.",
                )

            verification_method = "manual_supervised"

        # Load the existing custody history.
        all_events = list(
            db.scalars(
                select(CustodyEvent).where(
                    CustodyEvent.evidence_id == evidence.id
                )
            ).all()
        )

        # Do not append to an invalid chain.
        valid, broken_event_id = verify_event_chain(all_events)

        if not valid:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Custody history failed integrity verification. "
                    f"Problem event: {broken_event_id}"
                ),
            )

        # Find the actual end of the hash chain.
        try:
            latest_event = get_chain_tip(all_events)

        except ValueError as exc:
            raise HTTPException(
                status_code=409,
                detail="Custody history does not have a unique chain tip.",
            ) from exc

        # Create the new custody event.
        event = CustodyEvent(
            evidence_id=evidence.id,
            performed_by_personnel_id=current_personnel.id,
            from_personnel_id=current_personnel.id,
            to_personnel_id=recipient.id,
            device_id=payload.device_id,
            access_request_id=access_request.id,
            biometric_verification_id=(
                biometric.id if biometric else None
            ),
            transfer_reason=payload.transfer_reason.strip(),
            location=(
                payload.location.strip()
                if payload.location else None
            ),
            verification_method=verification_method,
            previous_hash=(
                latest_event.event_hash if latest_event else None
            ),
        )

        db.add(event)
        db.flush()

        # Calculate the event hash.
        event.event_hash = calculate_event_hash(event)

        evidence.status = "in_custody"

        # Record the transfer in the audit log.
        record_audit_event(
            db=db,
            action="CUSTODY_TRANSFER_RECORDED",
            resource_type="custody_event",
            outcome="success",
            personnel_id=current_personnel.id,
            resource_id=event.id,
            details=(
                f"Evidence {evidence.id} transferred from "
                f"{current_personnel.personnel_code} to "
                f"{recipient.personnel_code}; "
                f"method={verification_method}."
            ),
            correlation_id=access_request.correlation_id,
        )

        db.commit()
        db.refresh(event)

        return event

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to record custody transfer.",
        )


# ---------------------------------------------------------
# LIST CUSTODY EVENTS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[CustodyEventResponse],
)
def list_custody_events(
    evidence_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    """List custody events belonging to the user's organization."""

    query = (
        select(CustodyEvent)
        .join(
            Evidence,
            CustodyEvent.evidence_id == Evidence.id,
        )
        .join(
            Case,
            Evidence.case_id == Case.id,
        )
        .where(
            Case.organization_id
            == current_personnel.organization_id
        )
    )

    if evidence_id is not None:
        query = query.where(
            CustodyEvent.evidence_id == evidence_id
        )

    query = (
        query.order_by(
            CustodyEvent.event_time.desc(),
            CustodyEvent.id.desc(),
        )
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(query).all())


# ---------------------------------------------------------
# VERIFY EVIDENCE CUSTODY INTEGRITY
# ---------------------------------------------------------

@router.get(
    "/evidence/{evidence_id}/integrity",
    response_model=CustodyIntegrityResponse,
)
def verify_evidence_custody_integrity(
    evidence_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    """Verify the complete hash chain for an evidence item."""

    evidence = db.get(Evidence, evidence_id)

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence was not found.",
        )

    case = db.get(Case, evidence.case_id)

    if case is None:
        raise HTTPException(
            status_code=409,
            detail="Evidence case was not found.",
        )

    _ensure_same_organization(
        current_personnel,
        case.organization_id,
    )

    events = list(
        db.scalars(
            select(CustodyEvent).where(
                CustodyEvent.evidence_id == evidence_id
            )
        ).all()
    )

    valid, broken_event_id = verify_event_chain(events)

    return CustodyIntegrityResponse(
        evidence_id=evidence_id,
        valid=valid,
        event_count=len(events),
        broken_event_id=broken_event_id,
        message=(
            "Custody event hash chain is valid."
            if valid
            else "Custody event hash chain verification failed."
        ),
    )


# ---------------------------------------------------------
# GET ONE CUSTODY EVENT
# ---------------------------------------------------------

@router.get(
    "/{event_id}",
    response_model=CustodyEventResponse,
)
def get_custody_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
):
    """Retrieve one custody event within the user's organization."""

    event = db.get(CustodyEvent, event_id)

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Custody event was not found.",
        )

    evidence = db.get(Evidence, event.evidence_id)

    case = db.get(Case, evidence.case_id) if evidence else None

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence case was not found.",
        )

    _ensure_same_organization(
        current_personnel,
        case.organization_id,
    )

    return event


# ---------------------------------------------------------
# CORRECT A CUSTODY EVENT
# ---------------------------------------------------------

@router.post(
    "/{event_id}/correct",
    response_model=CustodyCorrectionResponse,
)
def correct_custody_event(
    event_id: UUID,
    payload: CustodyCorrectionCreate,
    db: Session = Depends(get_db),
    current_personnel: Personnel = Depends(get_current_personnel),
    _role=Depends(require_roles("admin", "reviewer")),
):
    """
    Append a correction record linked to an existing custody event.

    The original custody event is never modified or deleted.
    """

    try:
        # Find the original custody event.
        original_event = db.get(CustodyEvent, event_id)

        if original_event is None:
            raise HTTPException(
                status_code=404,
                detail="Custody event was not found.",
            )

        # Lock the evidence row to prevent simultaneous chain updates.
        evidence = db.scalar(
            select(Evidence)
            .where(Evidence.id == original_event.evidence_id)
            .with_for_update()
        )

        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail="Evidence was not found.",
            )

        case = db.get(Case, evidence.case_id)

        if case is None:
            raise HTTPException(
                status_code=409,
                detail="Evidence case was not found.",
            )

        _ensure_same_organization(
            current_personnel,
            case.organization_id,
        )

        # Prevent multiple corrections of the same original event.
        existing_correction = db.scalar(
            select(CustodyEvent).where(
                CustodyEvent.corrects_event_id == original_event.id
            )
        )

        if existing_correction is not None:
            raise HTTPException(
                status_code=409,
                detail="This custody event has already been corrected.",
            )

        # Load and verify the complete custody history.
        events = list(
            db.scalars(
                select(CustodyEvent).where(
                    CustodyEvent.evidence_id == evidence.id
                )
            ).all()
        )

        valid, broken_event_id = verify_event_chain(events)

        if not valid:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Custody history has failed integrity verification. "
                    f"Problem event: {broken_event_id}"
                ),
            )

        # Find the actual end of the chain.
        try:
            latest_event = get_chain_tip(events)

        except ValueError as exc:
            raise HTTPException(
                status_code=409,
                detail="Custody history does not have a unique chain tip.",
            ) from exc

        # Create a new record. Do not edit the original event.
        correction_event = CustodyEvent(
            evidence_id=original_event.evidence_id,
            performed_by_personnel_id=current_personnel.id,
            from_personnel_id=original_event.from_personnel_id,
            to_personnel_id=original_event.to_personnel_id,
            device_id=original_event.device_id,
            access_request_id=None,
            biometric_verification_id=(
                original_event.biometric_verification_id
            ),
            transfer_reason=original_event.transfer_reason,
            location=original_event.location,
            verification_method=original_event.verification_method,
            previous_hash=(
                latest_event.event_hash if latest_event else None
            ),
            corrects_event_id=original_event.id,
            correction_reason=payload.correction_reason.strip(),
        )

        db.add(correction_event)
        db.flush()

        # Calculate the new correction event hash.
        correction_event.event_hash = calculate_event_hash(
            correction_event
        )

        # Record the correction in the audit log.
        record_audit_event(
            db=db,
            action="CUSTODY_EVENT_CORRECTED",
            resource_type="custody_event",
            outcome="success",
            personnel_id=current_personnel.id,
            resource_id=correction_event.id,
            details=(
                f"Correction appended for original event "
                f"{original_event.id}. "
                f"Reason: {payload.correction_reason.strip()}"
            ),
        )

        db.commit()
        db.refresh(correction_event)

        return CustodyCorrectionResponse(
            message=(
                "Correction recorded. The original custody event "
                "has been preserved."
            ),
            original_event_id=original_event.id,
            correction_event=correction_event,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to record custody correction.",
        )
