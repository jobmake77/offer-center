from uuid import UUID

from fastapi import Header


def get_current_user_id(x_user_id: str | None = Header(default=None)) -> UUID:
    if x_user_id:
        return UUID(x_user_id)

    return UUID("00000000-0000-0000-0000-000000000001")
