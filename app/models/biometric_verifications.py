
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BiometricVerification(Base):
    """Records the outcome of a personnel biometric verification."""

    __tablename__ = "biometric_verifications"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Nullable when the system cannot identify the person.
    personnel_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=True,
        index=True,
    )

    # Device that performed or reported the verification.
    device_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=True,
        index=True,
    )

    verification_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Examples: success, failed, error.
    result: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Reference connecting this verification to a requested operation.
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    verified_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
