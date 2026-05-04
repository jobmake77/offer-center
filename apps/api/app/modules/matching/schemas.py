from uuid import UUID

from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume_version_id: UUID
    force_refresh: bool = False
