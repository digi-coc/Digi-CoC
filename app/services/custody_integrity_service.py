import hashlib
import json
from uuid import UUID


def _canonical_event_payload(event) -> dict:
    """Create a consistent representation of a custody event."""

    event_time = event.event_time

    return {
        "id": str(event.id),
        "evidence_id": str(event.evidence_id),
        "performed_by_personnel_id": (
            str(event.performed_by_personnel_id)
            if event.performed_by_personnel_id else None
        ),
        "from_personnel_id": (
            str(event.from_personnel_id)
            if event.from_personnel_id else None
        ),
        "to_personnel_id": str(event.to_personnel_id),
        "device_id": (
            str(event.device_id) if event.device_id else None
        ),
        "access_request_id": (
            str(event.access_request_id)
            if event.access_request_id else None
        ),
        "biometric_verification_id": (
            str(event.biometric_verification_id)
            if event.biometric_verification_id else None
        ),
        "transfer_reason": event.transfer_reason,
        "location": event.location,
        "verification_method": event.verification_method,
        "event_time": event_time.isoformat() if event_time else None,
        "previous_hash": event.previous_hash,
        "corrects_event_id": (
            str(event.corrects_event_id)
            if event.corrects_event_id else None
        ),
        "correction_reason": event.correction_reason,
    }


def calculate_event_hash(event) -> str:
    """Calculate the SHA-256 hash of a custody event."""

    encoded = json.dumps(
        _canonical_event_payload(event),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def verify_event_chain(events: list) -> tuple[bool, UUID | None]:
    """
    Verify custody events using their previous_hash links.

    The first event must have no previous hash.
    Every later event must point to the hash of the preceding event.
    """

    if not events:
        return True, None

    # Index events by their own hash.
    events_by_hash = {}

    for event in events:
        if not event.event_hash:
            return False, event.id

        if event.event_hash in events_by_hash:
            return False, event.id

        events_by_hash[event.event_hash] = event

    # Find the first event in the chain.
    roots = [
        event for event in events
        if event.previous_hash is None
    ]

    if len(roots) != 1:
        return False, roots[0].id if roots else events[0].id

    current_event = roots[0]
    visited_ids = set()

    while current_event is not None:

        if current_event.id in visited_ids:
            return False, current_event.id

        visited_ids.add(current_event.id)

        calculated_hash = calculate_event_hash(current_event)

        if current_event.event_hash != calculated_hash:
            return False, current_event.id

        # Find the next event whose previous_hash points here.
        next_events = [
            event for event in events
            if event.previous_hash == current_event.event_hash
        ]

        if len(next_events) > 1:
            return False, next_events[0].id

        current_event = next_events[0] if next_events else None

    # Every event must belong to the same connected chain.
    if len(visited_ids) != len(events):
        for event in events:
            if event.id not in visited_ids:
                return False, event.id

    return True, None


def get_chain_tip(events: list):
    """Return the final event in a valid, connected hash chain."""

    if not events:
        return None

    referenced_hashes = {
        event.previous_hash
        for event in events
        if event.previous_hash is not None
    }

    tips = [
        event for event in events
        if event.event_hash not in referenced_hashes
    ]

    if len(tips) != 1:
        raise ValueError("Custody event chain has no unique tip.")

    return tips[0]
