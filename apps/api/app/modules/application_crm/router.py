from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.application_crm.models import Application, ApplicationEvent
from app.modules.application_crm.schemas import (
    ApplicationEventPayload,
    CreateApplicationPayload,
    ReminderPayload,
    UpdateApplicationPayload,
    UpdateStagePayload,
)
from app.modules.identity.service import ensure_user
from app.modules.job_intelligence.models import JobPosting
from app.shared.contracts import Envelope

router = APIRouter(tags=["application-crm"])


@router.post("/applications", response_model=Envelope[dict[str, str]])
def create_application(
    payload: CreateApplicationPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    application = Application(
        user_id=user_id,
        job_posting_id=payload.job_posting_id,
        resume_version_id=payload.resume_version_id,
        source_channel=payload.source_channel,
        current_stage=payload.current_stage,
    )
    session.add(application)
    session.flush()
    session.commit()
    return Envelope(data={"application_id": str(application.id), "job_posting_id": str(payload.job_posting_id)})


@router.get("/applications", response_model=Envelope[list[dict]])
def list_applications(
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[list[dict]]:
    ensure_user(session, user_id)
    applications = list(
        session.execute(
            select(Application, JobPosting.title)
            .join(JobPosting, Application.job_posting_id == JobPosting.id, isouter=True)
            .where(Application.user_id == user_id)
            .order_by(Application.updated_at.desc())
        )
    )
    return Envelope(
        data=[
            {
                "id": str(application.id),
                "job_title": title or "Imported Job",
                "company_name": "Unknown Company",
                "current_stage": application.current_stage,
            }
            for application, title in applications
        ]
    )


@router.get("/applications/{application_id}", response_model=Envelope[dict])
def get_application(
    application_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    events = list(
        session.scalars(
            select(ApplicationEvent)
            .where(ApplicationEvent.application_id == application.id)
            .order_by(ApplicationEvent.event_time.desc())
        )
    )
    return Envelope(
        data={
            "id": str(application.id),
            "job_posting_id": str(application.job_posting_id),
            "current_stage": application.current_stage,
            "linked_assets": [],
            "linked_events": [
                {
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "event_time": event.event_time.isoformat(),
                    "payload": event.payload,
                }
                for event in events
            ],
            "linked_interview_summary": None,
        }
    )


@router.patch("/applications/{application_id}", response_model=Envelope[dict])
def update_application(
    application_id: UUID,
    payload: UpdateApplicationPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    session.commit()
    return Envelope(data={"id": str(application_id), **payload.model_dump(exclude_unset=True, mode="json")})


@router.patch("/applications/{application_id}/stage", response_model=Envelope[dict])
def update_application_stage(
    application_id: UUID,
    payload: UpdateStagePayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application.current_stage = payload.current_stage
    event = ApplicationEvent(
        application_id=application.id,
        event_type="stage_changed",
        event_time=payload.event_time,
        payload={"current_stage": payload.current_stage, "note": payload.note},
    )
    session.add(event)
    session.commit()
    return Envelope(data={"id": str(application_id), **payload.model_dump(mode="json")})


@router.post("/applications/{application_id}/events", response_model=Envelope[dict])
def create_application_event(
    application_id: UUID,
    payload: ApplicationEventPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    event = ApplicationEvent(
        application_id=application.id,
        event_type=payload.event_type,
        event_time=payload.event_time,
        payload=payload.payload,
    )
    session.add(event)
    session.commit()
    return Envelope(data={"application_id": str(application_id), **payload.model_dump(mode="json")})


@router.post("/applications/{application_id}/reminders", response_model=Envelope[dict])
def create_application_reminder(
    application_id: UUID,
    payload: ReminderPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    application = session.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.id == application_id,
        )
    )
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application.next_followup_at = payload.next_followup_at
    session.commit()
    return Envelope(data={"application_id": str(application_id), **payload.model_dump(mode="json")})
