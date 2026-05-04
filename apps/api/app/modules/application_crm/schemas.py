from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ApplicationStage = Literal[
    "draft",
    "ready_to_apply",
    "applied",
    "hr_replied",
    "interview",
    "offer",
    "rejected",
    "archived",
]


class CreateApplicationPayload(BaseModel):
    job_posting_id: UUID
    resume_version_id: UUID
    source_channel: str
    current_stage: ApplicationStage = "draft"


class UpdateApplicationPayload(BaseModel):
    contact_name: str | None = None
    contact_email: str | None = None
    notes: str | None = None
    next_followup_at: datetime | None = None


class UpdateStagePayload(BaseModel):
    current_stage: ApplicationStage
    event_time: datetime
    note: str | None = None


class ApplicationEventPayload(BaseModel):
    event_type: str
    event_time: datetime
    payload: dict = Field(default_factory=dict)


class ReminderPayload(BaseModel):
    next_followup_at: datetime
