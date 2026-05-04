from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.job_intelligence.models import JobPosting, JobRawInput


def infer_title_from_text(raw_content: str | None, fallback: str) -> str:
    if raw_content:
        for line in raw_content.splitlines():
            normalized = line.strip()
            if normalized:
                return normalized[:120]
    return fallback


def infer_title_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc or "Imported URL"
    path = parsed.path.strip("/").split("/")[-1] if parsed.path else ""
    suffix = f" / {path}" if path else ""
    return f"{host}{suffix}"[:120]


def create_job_import(
    session: Session,
    *,
    user_id: UUID,
    source_type: str,
    raw_content: str | None,
    source_ref: str | None = None,
    structured_jd: dict | None = None,
    hidden_signals: dict | None = None,
    skill_tags: list[str] | None = None,
    responsibility_tags: list[str] | None = None,
    risk_flags: list[str] | None = None,
    quality_score: float | None = None,
) -> tuple[JobRawInput, JobPosting]:
    raw_input = JobRawInput(
        user_id=user_id,
        source_type=source_type,
        source_ref=source_ref,
        raw_content=raw_content,
        ingestion_status="pending",
    )
    session.add(raw_input)
    session.flush()

    title_fallback = infer_title_from_url(source_ref or "") if source_type == "url" else "Imported Job"
    inferred_title = infer_title_from_text(raw_content, title_fallback)
    title = (structured_jd or {}).get("title") or inferred_title
    now = datetime.now(timezone.utc)

    job = JobPosting(
        user_id=user_id,
        raw_input_id=raw_input.id,
        title=title,
        normalized_title=(structured_jd or {}).get("normalized_title") or title.lower(),
        description_text=raw_content,
        city=structured_jd.get("city") if structured_jd else None,
        country=structured_jd.get("country") if structured_jd else None,
        remote_type=structured_jd.get("remote_type") if structured_jd else None,
        salary_min=structured_jd.get("salary_min") if structured_jd else None,
        salary_max=structured_jd.get("salary_max") if structured_jd else None,
        salary_currency=structured_jd.get("salary_currency") if structured_jd else None,
        experience_min_years=structured_jd.get("experience_min_years") if structured_jd else None,
        experience_max_years=structured_jd.get("experience_max_years") if structured_jd else None,
        education_requirement=structured_jd.get("education_requirement") if structured_jd else None,
        employment_type=structured_jd.get("employment_type") if structured_jd else None,
        structured_jd=structured_jd or {"source_type": source_type, "import_status": "raw"},
        skill_tags=skill_tags or [],
        responsibility_tags=responsibility_tags or [],
        hidden_signals=hidden_signals or {"needs_review": True},
        risk_flags=risk_flags or [],
        freshness_score=100.0,
        quality_score=quality_score if quality_score is not None else (60.0 if raw_content else 40.0),
        status="active",
        published_at=now,
        last_seen_at=now,
    )
    session.add(job)
    session.flush()
    return raw_input, job


def list_jobs_for_user(session: Session, user_id: UUID) -> list[JobPosting]:
    statement = (
        select(JobPosting)
        .where(JobPosting.user_id == user_id, JobPosting.status == "active")
        .order_by(JobPosting.published_at.desc().nullslast(), JobPosting.created_at.desc())
    )
    return list(session.scalars(statement))


def get_job_for_user(session: Session, user_id: UUID, job_id: UUID) -> JobPosting | None:
    statement = select(JobPosting).where(JobPosting.user_id == user_id, JobPosting.id == job_id)
    return session.scalar(statement)
