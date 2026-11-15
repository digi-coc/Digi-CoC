from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Organization(Base):
    """
    Represents a forensic laboratory or organization
    using the Digi-CoC system.
    """

    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    organization_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    address: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active"
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )