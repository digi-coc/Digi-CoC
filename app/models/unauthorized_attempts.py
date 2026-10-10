
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UnauthorizedAttempt(Base):
    """Records denied operations and security-relevant failures."""

    __tablename__ = "unauthorized_attempts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Nullable: the tag or person may not be recognized.
    evidence_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id"),
        nullable=True,
        index=True,
    )

    personnel_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=True,
        index=True,
    )

    # Optional reference to the device that initiated the attempt.
    device_identifier: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    attempt_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    outcome: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="denied",
        server_default="denied",
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attempted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
