from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.resume_assets.models import Resume, ResumeVersion


def list_resumes_for_user(session: Session, user_id: UUID) -> list[Resume]:
    statement = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.is_master.desc(), Resume.created_at.desc())
    )
    return list(session.scalars(statement))


def get_resume_for_user(session: Session, user_id: UUID, resume_id: UUID) -> Resume | None:
    statement = select(Resume).where(Resume.user_id == user_id, Resume.id == resume_id)
    return session.scalar(statement)


def create_resume(
    session: Session,
    *,
    user_id: UUID,
    filename: str,
    content_type: str | None,
    parsed_text: str | None,
    parsed_json: dict | None = None,
    parser_status: str = "pending",
) -> Resume:
    resume = Resume(
        user_id=user_id,
        name=Path(filename).stem or "Imported Resume",
        source_file_type=content_type,
        parser_status=parser_status,
        parsed_text=parsed_text,
        parsed_json=parsed_json or {"filename": filename, "upload_mode": "manual"},
    )
    session.add(resume)
    session.flush()
    return resume


def create_resume_version(
    session: Session,
    *,
    user_id: UUID,
    resume: Resume,
    job_posting_id: UUID | None,
    version_type: str,
    instructions: str | None,
) -> ResumeVersion:
    version = ResumeVersion(
        resume_id=resume.id,
        user_id=user_id,
        job_posting_id=job_posting_id,
        version_name=f"{resume.name} / {version_type}",
        version_type=version_type,
        content_json={
            "resume_name": resume.name,
            "source_resume_id": str(resume.id),
            "source_resume_summary": resume.parsed_json,
            "source_resume_text": resume.parsed_text or "",
            "instructions": instructions or "",
        },
        generation_status="succeeded",
    )
    session.add(version)
    session.flush()
    return version


def get_resume_version_for_user(session: Session, user_id: UUID, version_id: UUID) -> ResumeVersion | None:
    statement = select(ResumeVersion).where(
        ResumeVersion.user_id == user_id,
        ResumeVersion.id == version_id,
    )
    return session.scalar(statement)


def list_resume_versions_for_user(
    session: Session,
    *,
    user_id: UUID,
    resume_id: UUID | None = None,
    job_posting_id: UUID | None = None,
) -> list[ResumeVersion]:
    statement = select(ResumeVersion).where(ResumeVersion.user_id == user_id)

    if resume_id is not None:
        statement = statement.where(ResumeVersion.resume_id == resume_id)

    if job_posting_id is not None:
        statement = statement.where(ResumeVersion.job_posting_id == job_posting_id)

    statement = statement.order_by(ResumeVersion.updated_at.desc())
    return list(session.scalars(statement))


def update_resume_version_content(
    session: Session,
    *,
    version: ResumeVersion,
    content_json: dict,
) -> ResumeVersion:
    version.content_json = content_json
    session.flush()
    return version
