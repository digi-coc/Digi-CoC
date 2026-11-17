
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    Sequence,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


fingerprint_id_sequence = Sequence(
    "biometric_fingerprint_id_seq",
    start=1001,
    increment=1,
)


class BiometricTemplate(Base):
    """Stores encrypted fingerprint templates linked to personnel."""

    __tablename__ = "biometric_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    fingerprint_id: Mapped[int] = mapped_column(
        BigInteger,
        fingerprint_id_sequence,
        server_default=fingerprint_id_sequence.next_value(),
        nullable=False,
    )

    personnel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    finger_position: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    sensor_model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="R307S",
        server_default="R307S",
    )

    template_format: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Only encrypted template bytes are stored here.
    template_data: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    template_checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    encryption_key_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
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

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id", ondelete="SET NULL"),
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
        UniqueConstraint(
            "fingerprint_id",
            name="uq_biometric_templates_fingerprint_id",
        ),
        CheckConstraint(
            "length(template_checksum) = 64",
            name="ck_biometric_template_checksum_length",
        ),
        CheckConstraint(
            "length(finger_position) > 0",
            name="ck_biometric_template_finger_position",
        ),
        CheckConstraint(
            "length(template_format) > 0",
            name="ck_biometric_template_format",
        ),
        CheckConstraint(
            "(is_active = TRUE AND revoked_at IS NULL) "
            "OR (is_active = FALSE AND revoked_at IS NOT NULL)",
            name="ck_biometric_template_revocation_state",
        ),
        Index(
            "uq_active_biometric_personnel_finger",
            "personnel_id",
            "finger_position",
            unique=True,
            postgresql_where=text("is_active = TRUE"),
        ),
    )
