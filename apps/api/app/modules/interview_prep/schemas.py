from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateInterviewPayload(BaseModel):
    application_id: UUID
    round_name: str
    interview_type: str
    scheduled_at: datetime
    interviewer_names: list[str] = Field(default_factory=list)


class UpdateInterviewPayload(BaseModel):
    status: str | None = None
    notes: str | None = None
