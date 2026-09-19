from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.schemas.schemas import NextQuestionOut, AnswerIn, AnswerAck, CompleteAck
from app.services import session_service

router = APIRouter(prefix="/api/sessions", tags=["interview"])


@router.get("/{session_id}/next-question", response_model=NextQuestionOut)
def next_question(session_id: str, db: DBSession = Depends(get_db)):
    try:
        result = session_service.get_next_question(db, session_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        # Retrieval/generation failure (e.g. missing KB, LLM API error)
        raise HTTPException(status_code=502, detail=str(e))
    return NextQuestionOut(**result)


@router.post("/{session_id}/answers", response_model=AnswerAck)
def submit_answer(session_id: str, payload: AnswerIn, db: DBSession = Depends(get_db)):
    try:
        session_service.submit_answer(
            db, question_id=payload.question_id, answer_text=payload.answer_text
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return AnswerAck()


@router.post("/{session_id}/complete", response_model=CompleteAck)
def complete_session(session_id: str, db: DBSession = Depends(get_db)):
    try:
        session_service.complete_session(db, session_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return CompleteAck()
