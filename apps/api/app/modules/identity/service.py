from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.identity.models import User


def ensure_user(session: Session, user_id: UUID) -> User:
    existing = session.scalar(select(User).where(User.id == user_id))
    if existing is not None:
        return existing

    email = f"scaffold+{str(user_id).replace('-', '')[:12]}@example.com"
    user = User(id=user_id, email=email, name="Scaffold User")
    session.add(user)
    session.flush()
    return user
