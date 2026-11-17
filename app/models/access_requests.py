import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.base import Base


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    evidence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id"),
        nullable=False,
        index=True,
    )

    personnel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=False,
        index=True,
    )

    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("devices.id"),
        nullable=True,
    )

    request_reason = Column(Text, nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    correlation_id = Column(String(100), nullable=True, index=True)

    # Review information
    reviewed_by_personnel_id = Column(
        UUID(as_uuid=True),
        ForeignKey("personnel.id"),
        nullable=True,
    )

    decision_reason = Column(Text, nullable=True)

    decided_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )