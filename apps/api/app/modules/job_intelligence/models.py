from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.shared.models import utcnow

SOURCE_TYPE_VALUES = ("paste", "url", "upload", "email", "crawler")
PARSER_STATUS_VALUES = ("pending", "running", "succeeded", "failed")
JOB_STATUS_VALUES = ("active", "archived", "hidden")


class JobRawInput(Base):
    __tablename__ = "job_raw_inputs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    source_type: Mapped[str] = mapped_column(ENUM(*SOURCE_TYPE_VALUES, name="source_type", create_type=False))
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingestion_status: Mapped[str] = mapped_column(
        ENUM(*PARSER_STATUS_VALUES, name="parser_status", create_type=False), default="pending"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    company_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    raw_input_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    dedupe_group_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(Text)
    normalized_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True)
    remote_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_min: Mapped[int | None] = mapped_column(nullable=True)
    salary_max: Mapped[int | None] = mapped_column(nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_min_years: Mapped[int | None] = mapped_column(nullable=True)
    experience_max_years: Mapped[int | None] = mapped_column(nullable=True)
    education_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    employment_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_jd: Mapped[dict] = mapped_column(JSONB, default=dict)
    skill_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    responsibility_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    hidden_signals: Mapped[dict] = mapped_column(JSONB, default=dict)
    risk_flags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    freshness_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(ENUM(*JOB_STATUS_VALUES, name="job_status", create_type=False), default="active")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
