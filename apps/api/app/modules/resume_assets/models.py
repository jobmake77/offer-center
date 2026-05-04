from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.shared.models import utcnow

PARSER_STATUS_VALUES = ("pending", "running", "succeeded", "failed")
RESUME_VERSION_TYPE_VALUES = ("master", "manual", "ai_tailored")
TASK_STATUS_VALUES = ("queued", "running", "succeeded", "failed", "cancelled")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    name: Mapped[str] = mapped_column(Text)
    source_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    parser_status: Mapped[str] = mapped_column(
        ENUM(*PARSER_STATUS_VALUES, name="parser_status", create_type=False), default="pending"
    )
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_master: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    resume_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    job_posting_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    version_name: Mapped[str] = mapped_column(Text)
    version_type: Mapped[str] = mapped_column(
        ENUM(*RESUME_VERSION_TYPE_VALUES, name="resume_version_type", create_type=False), default="ai_tailored"
    )
    content_json: Mapped[dict] = mapped_column(JSONB, default=dict)
    rendered_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    export_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_status: Mapped[str] = mapped_column(
        ENUM(*TASK_STATUS_VALUES, name="task_status", create_type=False), default="queued"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
