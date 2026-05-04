from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.identity.service import ensure_user
from app.modules.job_intelligence.repository import get_job_for_user
from app.modules.matching.repository import (
    create_match_report,
    get_match_report_for_user,
    get_resume_version_for_match,
    list_match_reports_for_job,
    serialize_match_report,
)
from app.modules.matching.schemas import MatchRequest
from app.shared.contracts import Envelope

router = APIRouter(tags=["matching"])


@router.post("/jobs/{job_id}/match", response_model=Envelope[dict[str, str]])
def generate_match(
    job_id: UUID,
    payload: MatchRequest,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    job = get_job_for_user(session, user_id, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    resume_version = get_resume_version_for_match(
        session,
        user_id=user_id,
        version_id=payload.resume_version_id,
    )
    if resume_version is None:
        raise HTTPException(status_code=404, detail="Resume version not found")

    report = create_match_report(
        session,
        user_id=user_id,
        job=job,
        resume_version=resume_version,
    )
    session.commit()
    return Envelope(
        data={
            "job_id": str(job_id),
            "resume_version_id": str(payload.resume_version_id),
            "task_id": str(report.id),
            "status": "created",
        }
    )


@router.get("/jobs/{job_id}/match-reports", response_model=Envelope[list[dict]])
def list_match_reports(
    job_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[list[dict]]:
    ensure_user(session, user_id)
    reports = list_match_reports_for_job(session, user_id=user_id, job_id=job_id)
    return Envelope(data=[serialize_match_report(report) for report in reports])


@router.get("/match-reports/{report_id}", response_model=Envelope[dict])
def get_match_report(
    report_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    report = get_match_report_for_user(session, user_id=user_id, report_id=report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Match report not found")

    return Envelope(data=serialize_match_report(report))


@router.post("/match-reports/{report_id}/generate-actions", response_model=Envelope[dict[str, str]])
def generate_actions(report_id: str) -> Envelope[dict[str, str]]:
    return Envelope(data={"report_id": report_id, "status": "queued"})
