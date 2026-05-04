from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.application_crm.models import Application
from app.modules.interview_prep.models import Interview
from app.modules.job_intelligence.models import JobPosting


def get_dashboard_overview_for_user(session: Session, user_id: UUID) -> dict:
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)
    end_of_today = datetime.combine(now.date(), datetime.max.time(), tzinfo=timezone.utc)

    new_jobs_24h = session.scalar(
        select(func.count()).select_from(JobPosting).where(
            JobPosting.user_id == user_id,
            JobPosting.created_at >= since,
            JobPosting.status == "active",
        )
    ) or 0

    ready_to_apply = session.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == user_id,
            Application.current_stage == "ready_to_apply",
        )
    ) or 0

    followups_due_today = session.scalar(
        select(func.count()).select_from(Application).where(
            Application.user_id == user_id,
            Application.next_followup_at.is_not(None),
            Application.next_followup_at <= end_of_today,
        )
    ) or 0

    interviews_upcoming = session.scalar(
        select(func.count())
        .select_from(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(
            Application.user_id == user_id,
            Interview.scheduled_at.is_not(None),
            Interview.scheduled_at >= now,
            Interview.status != "cancelled",
        )
    ) or 0

    top_jobs = list(
        session.execute(
            select(JobPosting.id, JobPosting.title)
            .where(JobPosting.user_id == user_id, JobPosting.status == "active")
            .order_by(
                JobPosting.freshness_score.desc().nullslast(),
                JobPosting.quality_score.desc().nullslast(),
                JobPosting.created_at.desc(),
            )
            .limit(3)
        )
    )

    return {
        "new_jobs_24h": int(new_jobs_24h),
        "ready_to_apply": int(ready_to_apply),
        "followups_due_today": int(followups_due_today),
        "interviews_upcoming": int(interviews_upcoming),
        "top_recommendations": [
            {"id": f"job-{job_id}", "title": f"Review {title}"} for job_id, title in top_jobs
        ],
    }
