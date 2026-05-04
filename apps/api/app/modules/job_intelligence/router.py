from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.ai_gateway.analysis import AIProviderError, parse_job_with_ai
from app.modules.application_crm.models import Application
from app.modules.identity.service import ensure_user
from app.modules.job_intelligence.repository import create_job_import, get_job_for_user, list_jobs_for_user
from app.modules.job_intelligence.schemas import (
    FavoritePayload,
    JobImportPayload,
    JobImportUrlPayload,
    JobListItem,
)
from app.modules.matching.models import MatchReport
from app.modules.matching.repository import serialize_match_report
from app.shared.contracts import Envelope
from app.shared.tasks import enqueue_task

router = APIRouter(tags=["job-intelligence"])


@router.post("/jobs/import", response_model=Envelope[dict[str, str]])
def import_job(
    payload: JobImportPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    structured_jd: dict | None = None
    hidden_signals: dict | None = None
    skill_tags: list[str] | None = None
    responsibility_tags: list[str] | None = None
    risk_flags: list[str] | None = None
    quality_score: float | None = None

    if payload.raw_content:
        try:
            parsed = parse_job_with_ai(payload.raw_content)
            structured_jd = {
                "source_type": payload.source_type,
                "import_status": "ai_parsed",
                **parsed,
            }
            hidden_signals = parsed.get("hidden_signals") or {}
            skill_tags = parsed.get("skill_tags") or []
            responsibility_tags = parsed.get("responsibility_tags") or []
            risk_flags = parsed.get("risk_flags") or []
            quality_score = float(parsed.get("quality_score")) if parsed.get("quality_score") is not None else None
        except (AIProviderError, ValueError, TypeError):
            structured_jd = None

    _, job = create_job_import(
        session,
        user_id=user_id,
        source_type=payload.source_type,
        raw_content=payload.raw_content,
        structured_jd=structured_jd,
        hidden_signals=hidden_signals,
        skill_tags=skill_tags,
        responsibility_tags=responsibility_tags,
        risk_flags=risk_flags,
        quality_score=quality_score,
    )
    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="parse_job",
        target_type="job_posting",
        target_id=job.id,
        input_payload={"source_type": payload.source_type},
    )
    session.commit()
    return Envelope(
        data={
            "job_id": str(job.id),
            "source_type": payload.source_type,
            "task_id": str(task.id),
            "status": task.status,
        }
    )


@router.post("/jobs/import-url", response_model=Envelope[dict[str, str]])
def import_job_url(
    payload: JobImportUrlPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    _, job = create_job_import(
        session,
        user_id=user_id,
        source_type="url",
        raw_content=None,
        source_ref=payload.url,
    )
    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="parse_job",
        target_type="job_posting",
        target_id=job.id,
        input_payload={"url": payload.url},
    )
    session.commit()
    return Envelope(data={"job_id": str(job.id), "url": payload.url, "task_id": str(task.id)})


@router.get("/jobs", response_model=Envelope[list[JobListItem]])
def list_jobs(
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[list[JobListItem]]:
    ensure_user(session, user_id)
    jobs = list_jobs_for_user(session, user_id)
    data = [
        JobListItem(
            id=str(job.id),
            title=job.title,
            company_name="Unknown Company",
            city=job.city or "Unknown",
            score=int(job.quality_score or 0),
            risk_level="review" if job.risk_flags else "low",
        )
        for job in jobs
    ]
    return Envelope(data=data)


@router.get("/jobs/{job_id}", response_model=Envelope[dict])
def get_job(
    job_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    job = get_job_for_user(session, user_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    application = session.scalar(
        select(Application)
        .where(
            Application.user_id == user_id,
            Application.job_posting_id == job.id,
        )
        .order_by(Application.updated_at.desc())
        .limit(1)
    )
    latest_report = session.scalar(
        select(MatchReport)
        .where(
            MatchReport.user_id == user_id,
            MatchReport.job_posting_id == job.id,
        )
        .order_by(MatchReport.created_at.desc())
        .limit(1)
    )

    return Envelope(
        data={
            "id": str(job.id),
            "title": job.title,
            "structured_jd": job.structured_jd,
            "company_summary": {},
            "current_application_summary": {
                "id": str(application.id),
                "current_stage": application.current_stage,
                "resume_version_id": str(application.resume_version_id) if application.resume_version_id else None,
            }
            if application
            else None,
            "latest_match_report_summary": serialize_match_report(latest_report) if latest_report else None,
        }
    )


@router.post("/jobs/{job_id}/reparse", response_model=Envelope[dict[str, str]])
def reparse_job(
    job_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    job = get_job_for_user(session, user_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="parse_job",
        target_type="job_posting",
        target_id=job.id,
        input_payload={"job_id": str(job.id)},
    )
    session.commit()
    return Envelope(data={"job_id": str(job.id), "task_id": str(task.id), "status": task.status})


@router.post("/jobs/{job_id}/archive", response_model=Envelope[dict[str, str]])
def archive_job(
    job_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    job = get_job_for_user(session, user_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "archived"
    session.commit()
    return Envelope(data={"job_id": str(job.id), "status": job.status})


@router.post("/jobs/{job_id}/favorite", response_model=Envelope[dict[str, str | bool]])
def favorite_job(
    job_id: UUID,
    payload: FavoritePayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str | bool]]:
    ensure_user(session, user_id)
    job = get_job_for_user(session, user_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_favorite = payload.favorite
    session.commit()
    return Envelope(data={"job_id": str(job.id), "favorite": payload.favorite})
