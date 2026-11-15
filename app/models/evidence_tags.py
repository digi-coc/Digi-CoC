
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


class EvidenceTag(Base):
    """Represents an RFID/NFC tag assigned to evidence."""

    __tablename__ = "evidence_tags"

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

    tag_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # Store the identifier read from the physical tag.
    tag_identifier: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    assigned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "tag_type IN ('RFID', 'NFC')",
            name="ck_evidence_tags_type",
        ),
    )
