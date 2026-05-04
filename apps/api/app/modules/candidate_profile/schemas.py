from pydantic import BaseModel, Field


class ProfilePayload(BaseModel):
    headline: str | None = None
    years_of_experience: int | None = None
    current_city: str | None = None
    target_roles: list[str] = Field(default_factory=list)
    seniority_level: str | None = None
    summary: str | None = None
    skills: dict = Field(default_factory=dict)


class PreferencesPayload(BaseModel):
    preferred_cities: list[str] = Field(default_factory=list)
    remote_preference: str | None = None
    salary_expectation_min: int | None = None
    salary_expectation_max: int | None = None
    target_industries: list[str] = Field(default_factory=list)
    target_company_stages: list[str] = Field(default_factory=list)
    deal_breakers: dict = Field(default_factory=dict)
    work_style_preferences: dict = Field(default_factory=dict)
    importance_weights: dict = Field(default_factory=dict)

