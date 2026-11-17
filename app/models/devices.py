from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Device(Base):
    """Represents a registered hardware device used by Digi-CoC."""

    __tablename__ = "devices"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    device_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    device_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    # SHA-256 hash of the device's API key.
    # The original key is never stored in the database.
    api_key_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    last_seen_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "device_type IN ('ESP32_CONTROLLER', "
            "'FINGERPRINT_SENSOR', 'RFID_READER', "
            "'NFC_READER', 'OTHER')",
            name="ck_devices_device_type",
        ),
    )
