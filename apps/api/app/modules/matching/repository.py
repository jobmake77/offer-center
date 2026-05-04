from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ai_gateway.analysis import AIProviderError, build_match_report_with_ai
from app.modules.ai_gateway.client import get_ai_model_label
from app.modules.job_intelligence.models import JobPosting
from app.modules.matching.models import MatchReport
from app.modules.resume_assets.models import Resume, ResumeVersion


def _clamp(score: float) -> float:
    return max(0.0, min(100.0, round(score, 2)))


def _report_to_dict(report: MatchReport) -> dict:
    return {
        "id": str(report.id),
        "scores": {
            "hard_fit": float(report.hard_fit_score or 0),
            "skill_fit": float(report.skill_fit_score or 0),
            "work_content_fit": float(report.work_content_fit_score or 0),
            "career_fit": float(report.career_fit_score or 0),
            "risk_adjusted_value": float(report.risk_adjusted_value_score or 0),
            "overall": float(report.overall_score or 0),
        },
        "missing_requirements": report.missing_requirements,
        "strengths": report.strengths,
        "weaknesses": report.weaknesses,
        "tailored_suggestions": report.tailored_suggestions,
        "evidence": report.evidence,
    }


def get_resume_version_for_match(
    session: Session,
    *,
    user_id: UUID,
    version_id: UUID,
) -> ResumeVersion | None:
    statement = select(ResumeVersion).where(
        ResumeVersion.user_id == user_id,
        ResumeVersion.id == version_id,
    )
    return session.scalar(statement)


def create_match_report(
    session: Session,
    *,
    user_id: UUID,
    job: JobPosting,
    resume_version: ResumeVersion,
) -> MatchReport:
    source_resume_id = resume_version.content_json.get("source_resume_id")
    source_resume = None
    if isinstance(source_resume_id, str):
        try:
            source_resume = session.scalar(
                select(Resume).where(Resume.user_id == user_id, Resume.id == UUID(source_resume_id))
            )
        except ValueError:
            source_resume = None

    try:
        llm_report = build_match_report_with_ai(job, source_resume, resume_version)
        scores = llm_report.get("scores") or {}

        report = MatchReport(
            user_id=user_id,
            job_posting_id=job.id,
            resume_version_id=resume_version.id,
            hard_fit_score=_clamp(float(scores.get("hard_fit", 0))),
            skill_fit_score=_clamp(float(scores.get("skill_fit", 0))),
            work_content_fit_score=_clamp(float(scores.get("work_content_fit", 0))),
            career_fit_score=_clamp(float(scores.get("career_fit", 0))),
            risk_adjusted_value_score=_clamp(float(scores.get("risk_adjusted_value", 0))),
            overall_score=_clamp(float(scores.get("overall", 0))),
            missing_requirements=llm_report.get("missing_requirements") or [],
            strengths=llm_report.get("strengths") or [],
            weaknesses=llm_report.get("weaknesses") or [],
            tailored_suggestions=llm_report.get("tailored_suggestions") or [],
            evidence=llm_report.get("evidence") or [],
            model_version=get_ai_model_label(),
        )
        session.add(report)
        session.flush()
        return report
    except (AIProviderError, TypeError, ValueError):
        pass

    base_quality = float(job.quality_score or Decimal("50"))
    content_bonus = 12.0 if resume_version.content_json else 0.0
    instruction_bonus = 6.0 if resume_version.content_json.get("instructions") else 0.0
    risk_penalty = 8.0 if job.risk_flags else 0.0

    hard_fit = _clamp(base_quality + content_bonus - risk_penalty)
    skill_fit = _clamp(base_quality + instruction_bonus)
    work_content_fit = _clamp(base_quality + 10.0)
    career_fit = _clamp(base_quality + 8.0)
    risk_adjusted_value = _clamp(base_quality - risk_penalty)
    overall = _clamp((hard_fit + skill_fit + work_content_fit + career_fit + risk_adjusted_value) / 5)

    report = MatchReport(
        user_id=user_id,
        job_posting_id=job.id,
        resume_version_id=resume_version.id,
        hard_fit_score=hard_fit,
        skill_fit_score=skill_fit,
        work_content_fit_score=work_content_fit,
        career_fit_score=career_fit,
        risk_adjusted_value_score=risk_adjusted_value,
        overall_score=overall,
        missing_requirements=[] if overall >= 70 else ["Need manual review for scope clarity"],
        strengths=[
            "Resume version is linked to the target job",
            "Job is already normalized into the workspace",
        ],
        weaknesses=[] if not job.risk_flags else ["Risk flags require manual review"],
        tailored_suggestions=[
            "Emphasize architecture ownership",
            "Make role scope and cross-team impact explicit",
        ],
        evidence=[
            {"type": "job_quality_score", "value": base_quality},
            {"type": "resume_version_id", "value": str(resume_version.id)},
        ],
        model_version="scaffold-v1",
    )
    session.add(report)
    session.flush()
    return report


def list_match_reports_for_job(session: Session, *, user_id: UUID, job_id: UUID) -> list[MatchReport]:
    statement = (
        select(MatchReport)
        .where(MatchReport.user_id == user_id, MatchReport.job_posting_id == job_id)
        .order_by(MatchReport.created_at.desc())
    )
    return list(session.scalars(statement))


def get_match_report_for_user(session: Session, *, user_id: UUID, report_id: UUID) -> MatchReport | None:
    statement = select(MatchReport).where(MatchReport.user_id == user_id, MatchReport.id == report_id)
    return session.scalar(statement)


def serialize_match_report(report: MatchReport) -> dict:
    return _report_to_dict(report)
