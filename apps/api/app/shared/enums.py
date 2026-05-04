from enum import StrEnum


class ApplicationStage(StrEnum):
    DRAFT = "draft"
    READY_TO_APPLY = "ready_to_apply"
    APPLIED = "applied"
    HR_REPLIED = "hr_replied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    ARCHIVED = "archived"

