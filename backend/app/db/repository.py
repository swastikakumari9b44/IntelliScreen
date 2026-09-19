"""
Repository layer.

Why this exists as its own layer: services should orchestrate business
logic (RAG pipeline, resume parsing, etc.) without knowing SQL/ORM
details. If we ever change how a query is written, or swap ORMs, only
this file changes -- services stay untouched.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import SessionRecord, QuestionRecord, AnswerRecord


# ---------- Sessions ----------

def create_session(
    db: Session, *, role: str, resume_filename: str,
    candidate_name: str | None, extracted_skills: list[str],
) -> SessionRecord:
    record = SessionRecord(
        role=role,
        resume_filename=resume_filename,
        candidate_name=candidate_name,
        extracted_skills=extracted_skills,
        status="in_progress",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_session(db: Session, session_id: str) -> SessionRecord | None:
    return db.query(SessionRecord).filter(SessionRecord.id == session_id).first()


def list_sessions(db: Session, limit: int = 50) -> list[SessionRecord]:
    return (
        db.query(SessionRecord)
        .order_by(SessionRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def complete_session(db: Session, session_id: str) -> SessionRecord | None:
    record = get_session(db, session_id)
    if record is None:
        return None
    record.status = "completed"
    record.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


# ---------- Questions ----------

def create_question(
    db: Session, *, session_id: str, question_text: str,
    source_chunk_ids: list[str], topic: str | None, sequence_number: int,
) -> QuestionRecord:
    record = QuestionRecord(
        session_id=session_id,
        question_text=question_text,
        source_chunk_ids=source_chunk_ids,
        topic=topic,
        sequence_number=sequence_number,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_question(db: Session, question_id: str) -> QuestionRecord | None:
    return db.query(QuestionRecord).filter(QuestionRecord.id == question_id).first()


def list_questions_for_session(db: Session, session_id: str) -> list[QuestionRecord]:
    return (
        db.query(QuestionRecord)
        .filter(QuestionRecord.session_id == session_id)
        .order_by(QuestionRecord.sequence_number.asc())
        .all()
    )


def count_questions_for_session(db: Session, session_id: str) -> int:
    return (
        db.query(QuestionRecord)
        .filter(QuestionRecord.session_id == session_id)
        .count()
    )


# ---------- Answers ----------

def create_answer(db: Session, *, question_id: str, answer_text: str) -> AnswerRecord:
    record = AnswerRecord(question_id=question_id, answer_text=answer_text)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_answer_for_question(db: Session, question_id: str) -> AnswerRecord | None:
    return db.query(AnswerRecord).filter(AnswerRecord.question_id == question_id).first()
