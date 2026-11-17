
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BiometricEnrollment(Base):
    """Links an enrolled fingerprint template to an authorised device."""

    __tablename__ = "biometric_enrollments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    personnel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=False,
        index=True,
    )

    template_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    enrollment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
    )

    enrolled_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    revoked_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "enrollment_status IN ('active', 'revoked')",
            name="ck_biometric_enrollment_status",
        ),
        UniqueConstraint(
            "device_id",
            "template_reference",
            name="uq_biometric_device_template_reference",
        ),
    )
