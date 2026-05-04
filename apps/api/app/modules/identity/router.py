from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.identity.service import ensure_user
from app.shared.contracts import Envelope

router = APIRouter(tags=["identity"])


@router.get("/me", response_model=Envelope[dict[str, str]])
def get_current_user(
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    user = ensure_user(session, user_id)
    session.commit()
    return Envelope(data={"user_id": str(user_id), "status": "scaffold"})
