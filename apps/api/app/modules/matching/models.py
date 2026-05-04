from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.shared.models import utcnow


class MatchReport(Base):
    __tablename__ = "match_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    job_posting_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    resume_version_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    hard_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    skill_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    work_content_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    career_fit_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_adjusted_value_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    missing_requirements: Mapped[list] = mapped_column(JSONB, default=list)
    strengths: Mapped[list] = mapped_column(JSONB, default=list)
    weaknesses: Mapped[list] = mapped_column(JSONB, default=list)
    tailored_suggestions: Mapped[list] = mapped_column(JSONB, default=list)
    evidence: Mapped[list] = mapped_column(JSONB, default=list)
    model_version: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
