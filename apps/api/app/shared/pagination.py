from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int = 0

