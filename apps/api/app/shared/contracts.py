from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Envelope(BaseModel, Generic[T]):
    data: T | None
    meta: dict[str, Any] = Field(default_factory=dict)
    error: ErrorPayload | None = None


class TaskAccepted(BaseModel):
    task_id: str
    status: str = "queued"

