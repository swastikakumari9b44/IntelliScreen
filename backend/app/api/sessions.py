from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.db import repository
from app.roles import get_role
from app.schemas.schemas import SessionCreateResponse, SessionSummaryOut, SessionDetailOut
from app.services import session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


@router.post("", response_model=SessionCreateResponse)
async def create_session(
    role: str = Form(...),
    candidate_name: str | None = Form(None),
    resume_file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    if get_role(role) is None:
        raise HTTPException(status_code=400, detail=f"Unknown role '{role}'.")

    resume_bytes = await resume_file.read()
    if len(resume_bytes) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Resume file too large (max 5MB).")

    try:
        result = session_service.start_session(
            db,
            role_id=role,
            candidate_name=candidate_name,
            resume_bytes=resume_bytes,
            resume_filename=resume_file.filename or "resume.pdf",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return SessionCreateResponse(**result)


@router.get("", response_model=list[SessionSummaryOut])
def list_sessions(db: DBSession = Depends(get_db)):
    records = repository.list_sessions(db)
    return [
        SessionSummaryOut(
            id=r.id, role=r.role, candidate_name=r.candidate_name,
            status=r.status, created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/{session_id}/summary", response_model=SessionDetailOut)
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    try:
        return session_service.build_summary(db, session_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
