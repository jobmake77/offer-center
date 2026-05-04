from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.modules.ai_gateway.analysis import AIProviderError, parse_resume_with_ai
from app.core.db import get_db
from app.core.security import get_current_user_id
from app.modules.identity.service import ensure_user
from app.modules.job_intelligence.repository import get_job_for_user
from app.modules.resume_assets.repository import (
    create_resume,
    create_resume_version as create_resume_version_record,
    get_resume_for_user,
    get_resume_version_for_user,
    list_resumes_for_user,
    list_resume_versions_for_user,
    update_resume_version_content,
)
from app.modules.resume_assets.schemas import (
    CreateResumeVersionPayload,
    ResumeItem,
    ResumeVersionItem,
    ResumeVersionPayload,
)
from app.shared.contracts import Envelope
from app.shared.tasks import enqueue_task

router = APIRouter(tags=["resume-assets"])


@router.get("/resumes", response_model=Envelope[list[ResumeItem]])
def list_resumes(
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[list[ResumeItem]]:
    ensure_user(session, user_id)
    resumes = list_resumes_for_user(session, user_id)
    data = [
        ResumeItem(
            id=str(resume.id),
            name=resume.name,
            is_master=resume.is_master,
            parser_status=resume.parser_status,
        )
        for resume in resumes
    ]
    return Envelope(data=data)


@router.get("/resume-versions", response_model=Envelope[list[ResumeVersionItem]])
def list_resume_versions(
    resume_id: UUID | None = Query(default=None),
    job_posting_id: UUID | None = Query(default=None),
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[list[ResumeVersionItem]]:
    ensure_user(session, user_id)
    versions = list_resume_versions_for_user(
        session,
        user_id=user_id,
        resume_id=resume_id,
        job_posting_id=job_posting_id,
    )
    return Envelope(
        data=[
            ResumeVersionItem(
                id=str(version.id),
                resume_id=str(version.resume_id),
                job_posting_id=str(version.job_posting_id) if version.job_posting_id else None,
                version_name=version.version_name,
                version_type=version.version_type,
                generation_status=version.generation_status,
            )
            for version in versions
        ]
    )


@router.post("/resumes/upload", response_model=Envelope[dict[str, str]])
async def upload_resume(
    file: UploadFile = File(...),
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    content = await file.read()
    parsed_text: str | None = None
    if file.content_type and file.content_type.startswith("text/"):
        parsed_text = content.decode("utf-8", errors="ignore")[:10000]

    parsed_json: dict | None = None
    parser_status = "pending"
    if parsed_text:
        try:
            parsed_json = {
                "filename": file.filename or "resume.txt",
                "upload_mode": "manual",
                "parser": "kimi",
                **parse_resume_with_ai(parsed_text),
            }
            parser_status = "succeeded"
        except AIProviderError:
            parsed_json = {"filename": file.filename or "resume.txt", "upload_mode": "manual"}
            parser_status = "pending"

    resume = create_resume(
        session,
        user_id=user_id,
        filename=file.filename or "resume.txt",
        content_type=file.content_type,
        parsed_text=parsed_text,
        parsed_json=parsed_json,
        parser_status=parser_status,
    )
    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="parse_resume",
        target_type="resume",
        target_id=resume.id,
        input_payload={"filename": file.filename, "content_type": file.content_type},
    )
    session.commit()
    return Envelope(data={"resume_id": str(resume.id), "task_id": str(task.id), "filename": file.filename or ""})


@router.get("/resumes/{resume_id}", response_model=Envelope[ResumeItem])
def get_resume(
    resume_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[ResumeItem]:
    ensure_user(session, user_id)
    resume = get_resume_for_user(session, user_id, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    return Envelope(
        data=ResumeItem(
            id=str(resume.id),
            name=resume.name,
            is_master=resume.is_master,
            parser_status=resume.parser_status,
        )
    )


@router.post("/resumes/{resume_id}/parse", response_model=Envelope[dict[str, str]])
def reparse_resume(
    resume_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    resume = get_resume_for_user(session, user_id, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    task = enqueue_task(
        session,
        user_id=user_id,
        task_type="parse_resume",
        target_type="resume",
        target_id=resume.id,
        input_payload={"resume_id": str(resume.id)},
    )
    session.commit()
    return Envelope(data={"resume_id": str(resume.id), "task_id": str(task.id), "status": task.status})


@router.post("/resumes/{resume_id}/versions", response_model=Envelope[dict[str, str]])
def create_resume_version(
    resume_id: UUID,
    payload: CreateResumeVersionPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    resume = get_resume_for_user(session, user_id, resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")

    if payload.job_posting_id is not None and get_job_for_user(session, user_id, payload.job_posting_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")

    version = create_resume_version_record(
        session,
        user_id=user_id,
        resume=resume,
        job_posting_id=payload.job_posting_id,
        version_type=payload.version_type,
        instructions=payload.instructions,
    )
    session.commit()
    return Envelope(
        data={
            "resume_id": str(resume_id),
            "version_id": str(version.id),
            "job_posting_id": str(payload.job_posting_id) if payload.job_posting_id else "",
            "version_type": payload.version_type,
        }
    )


@router.get("/resume-versions/{version_id}", response_model=Envelope[dict])
def get_resume_version(
    version_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    version = get_resume_version_for_user(session, user_id, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Resume version not found")

    return Envelope(
        data={
            "id": str(version.id),
            "resume_id": str(version.resume_id),
            "job_posting_id": str(version.job_posting_id) if version.job_posting_id else None,
            "version_name": version.version_name,
            "version_type": version.version_type,
            "content_json": version.content_json,
            "generation_status": version.generation_status,
        }
    )


@router.patch("/resume-versions/{version_id}", response_model=Envelope[dict])
def update_resume_version(
    version_id: UUID,
    payload: ResumeVersionPayload,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict]:
    ensure_user(session, user_id)
    version = get_resume_version_for_user(session, user_id, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Resume version not found")

    update_resume_version_content(session, version=version, content_json=payload.content_json)
    session.commit()
    return Envelope(data={"id": str(version_id), "content_json": payload.content_json})


@router.post("/resume-versions/{version_id}/export", response_model=Envelope[dict[str, str]])
def export_resume_version(
    version_id: UUID,
    user_id=Depends(get_current_user_id),
    session: Session = Depends(get_db),
) -> Envelope[dict[str, str]]:
    ensure_user(session, user_id)
    version = get_resume_version_for_user(session, user_id, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Resume version not found")

    version.generation_status = "queued"
    session.commit()
    return Envelope(data={"id": str(version_id), "status": "queued", "format": "pdf"})
