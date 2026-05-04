from fastapi import APIRouter

from app.modules.candidate_profile.schemas import PreferencesPayload, ProfilePayload
from app.shared.contracts import Envelope

router = APIRouter(tags=["candidate-profile"])


@router.get("/profile", response_model=Envelope[ProfilePayload])
def get_profile() -> Envelope[ProfilePayload]:
    return Envelope(data=ProfilePayload(headline="Candidate profile scaffold"))


@router.patch("/profile", response_model=Envelope[ProfilePayload])
def update_profile(payload: ProfilePayload) -> Envelope[ProfilePayload]:
    return Envelope(data=payload)


@router.get("/preferences", response_model=Envelope[PreferencesPayload])
def get_preferences() -> Envelope[PreferencesPayload]:
    return Envelope(data=PreferencesPayload())


@router.patch("/preferences", response_model=Envelope[PreferencesPayload])
def update_preferences(payload: PreferencesPayload) -> Envelope[PreferencesPayload]:
    return Envelope(data=payload)

