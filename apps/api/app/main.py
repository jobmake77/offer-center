from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.application_crm.router import router as application_crm_router
from app.modules.candidate_profile.router import router as candidate_profile_router
from app.modules.identity.router import router as identity_router
from app.modules.interview_prep.router import router as interview_prep_router
from app.modules.job_intelligence.router import router as job_intelligence_router
from app.modules.matching.router import router as matching_router
from app.modules.recommendation.router import router as recommendation_router
from app.modules.resume_assets.router import router as resume_assets_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Offer Center API",
        version="0.1.0",
        description="Backend API for the Offer Center job search workspace.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(identity_router, prefix="/api/v1")
    app.include_router(candidate_profile_router, prefix="/api/v1")
    app.include_router(resume_assets_router, prefix="/api/v1")
    app.include_router(job_intelligence_router, prefix="/api/v1")
    app.include_router(matching_router, prefix="/api/v1")
    app.include_router(application_crm_router, prefix="/api/v1")
    app.include_router(interview_prep_router, prefix="/api/v1")
    app.include_router(recommendation_router, prefix="/api/v1")

    return app


app = create_app()

