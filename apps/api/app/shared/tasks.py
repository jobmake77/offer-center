from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.shared.contracts import TaskAccepted
from app.shared.models import Task


def enqueue_stub_task() -> TaskAccepted:
    return TaskAccepted(task_id=str(uuid4()))


def enqueue_task(
    session: Session,
    *,
    user_id: UUID,
    task_type: str,
    target_type: str | None = None,
    target_id: UUID | None = None,
    input_payload: dict | None = None,
) -> Task:
    task = Task(
        user_id=user_id,
        task_type=task_type,
        target_type=target_type,
        target_id=target_id,
        status="queued",
        input=input_payload or {},
        output={},
    )
    session.add(task)
    session.flush()
    return task
