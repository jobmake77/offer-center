from uuid import UUID

from pydantic import BaseModel, Field


class ResumeItem(BaseModel):
    id: str
    name: str
    is_master: bool = False
    parser_status: str = "pending"


class CreateResumeVersionPayload(BaseModel):
    job_posting_id: UUID | None = None
    version_type: str = "ai_tailored"
    instructions: str | None = None


class ResumeVersionPayload(BaseModel):
    content_json: dict = Field(default_factory=dict)


class ResumeVersionItem(BaseModel):
    id: str
    resume_id: str
    job_posting_id: str | None = None
    version_name: str
    version_type: str
    generation_status: str
