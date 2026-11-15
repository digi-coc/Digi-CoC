
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Evidence(Base):
    """Represents a physical evidence item registered in Digi-CoC."""

    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # The case this evidence belongs to.
    case_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )

    # Human-readable evidence identifier, unique within a case.
    evidence_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    item_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="registered",
        server_default="registered",
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
            "case_id",
            "evidence_code",
            name="uq_evidence_case_code",
        ),
        CheckConstraint(
            "status IN ('registered', 'collected', 'in_custody', "
            "'transferred', 'released', 'archived')",
            name="ck_evidence_status",
        ),
    )
