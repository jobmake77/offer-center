from pydantic import BaseModel, Field


class JobImportPayload(BaseModel):
    source_type: str = "paste"
    raw_content: str | None = None


class JobImportUrlPayload(BaseModel):
    url: str


class JobListItem(BaseModel):
    id: str
    title: str
    company_name: str
    city: str
    score: int
    risk_level: str


class FavoritePayload(BaseModel):
    favorite: bool = True

