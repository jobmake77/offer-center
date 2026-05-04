from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.shared.models import utcnow

INTERVIEW_TYPE_VALUES = ("hr", "technical", "hiring_manager", "system_design", "other")


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    application_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    round_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    interview_type: Mapped[str] = mapped_column(
        ENUM(*INTERVIEW_TYPE_VALUES, name="interview_type", create_type=False), default="other"
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interviewer_names: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    status: Mapped[str] = mapped_column(String(32), default="scheduled")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
