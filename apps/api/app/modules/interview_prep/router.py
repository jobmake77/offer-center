from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.application_crm.models import Application
from app.modules.identity.service import ensure_user
from app.modules.interview_prep.models import Interview
from app.modules.interview_prep.schemas import CreateInterviewPayload, UpdateInterviewPayload
from app.shared.contracts import Envelope
from app.shared.tasks import enqueue_task

router = APIRouter(tags=["interview-prep"])


@router.post("/interviews", response_model=Envelope[dict])
def create_interview(
    payload: CreateInterviewPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == payload.application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    interview = Interview(
        application_id=application.id,
        round_name=payload.round_name,
        interview_type=payload.interview_type,
        scheduled_at=payload.scheduled_at,
        interviewer_names=payload.interviewer_names,
    )
    session.add(interview)
    session.flush()
    session.commit()
    return Envelope(data={"id": str(interview.id), **payload.model_dump(mode="json")})


@router.get("/interviews/{interview_id}", response_model=Envelope[dict])
def get_interview(
    interview_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    interview = session.scalar(
        select(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(Application.user_id == user_id, Interview.id == interview_id)
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    return Envelope(data={"id": str(interview.id), "status": interview.status, "latest_prep_asset": None})


@router.post("/interviews/{interview_id}/generate-prep", response_model=Envelope[dict[str, str]])
def generate_interview_prep(
    interview_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    interview = session.scalar(
        select(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(Application.user_id == user_id, Interview.id == interview_id)
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="generate_interview_prep",
        target_type="interview",
        target_id=interview.id,
        input_payload={"interview_id": str(interview.id)},
    )
    session.commit()
    return Envelope(data={"interview_id": str(interview_id), "task_id": str(task.id), "status": task.status})


@router.patch("/interviews/{interview_id}", response_model=Envelope[dict])
def update_interview(
    interview_id: UUID,
    payload: UpdateInterviewPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    interview = session.scalar(
        select(Interview)
        .join(Application, Interview.application_id == Application.id)
        .where(Application.user_id == user_id, Interview.id == interview_id)
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)

    session.commit()
    return Envelope(data={"id": str(interview_id), **payload.model_dump(exclude_unset=True, mode="json")})
