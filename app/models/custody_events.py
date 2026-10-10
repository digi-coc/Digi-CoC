
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CustodyEvent(Base):
    """Append-only record of an evidence custody event."""

    __tablename__ = "custody_events"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    evidence_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id"),
        nullable=False,
        index=True,
    )

    # Nullable because an initial custody assignment may have no sender.
    from_personnel_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=True,
    )

    to_personnel_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=False,
    )

    transfer_reason: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    verification_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    event_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Optional hash-chain fields. The service layer will calculate them.
    previous_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    event_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    # Corrections should reference the event being corrected.
    corrects_event_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("custody_events.id"),
        nullable=True,
    )

    correction_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "from_personnel_id IS NULL OR "
            "from_personnel_id <> to_personnel_id",
            name="ck_custody_different_personnel",
        ),
        CheckConstraint(
            "corrects_event_id IS NULL OR "
            "correction_reason IS NOT NULL",
            name="ck_custody_correction_reason",
        ),
    )
