from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.identity.service import ensure_user
from app.modules.recommendation.repository import get_dashboard_overview_for_user
from app.shared.contracts import Envelope

router = APIRouter(tags=["recommendation"])


@router.get("/dashboard/overview", response_model=Envelope[dict])
def get_dashboard_overview(
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    return Envelope(data=get_dashboard_overview_for_user(session, user_id))


@router.get("/dashboard/today-actions", response_model=Envelope[list[dict]])
def get_today_actions() -> Envelope[list[dict]]:
    return Envelope(
        data=[
            {"id": "action-1", "priority": 1, "title": "Review a newly imported role."},
            {"id": "action-2", "priority": 2, "title": "Send one overdue follow-up."},
        ]
    )


@router.get("/insights/pipeline", response_model=Envelope[dict])
def get_pipeline_insights() -> Envelope[dict]:
    return Envelope(data={"draft": 2, "applied": 3, "interview": 1})


@router.get("/insights/conversion", response_model=Envelope[dict])
def get_conversion_insights() -> Envelope[dict]:
    return Envelope(data={"reviewed_to_applied": 0.35, "applied_to_reply": 0.22, "reply_to_interview": 0.5})
