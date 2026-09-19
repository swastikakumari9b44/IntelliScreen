"""
Session service.

Orchestrates the interview lifecycle end-to-end, tying together resume
parsing, question generation, and persistence. This is the layer the
API routers call into -- routers stay thin (validation + delegation),
all real logic lives here and in the services it calls.
"""
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import repository
from app.roles import get_role
from app.services import resume_parser
from app.services.question_gen_service import generate_question

settings = get_settings()


def start_session(
    db: Session, *, role_id: str, candidate_name: str | None,
    resume_bytes: bytes, resume_filename: str,
) -> dict:
    role = get_role(role_id)
    if role is None:
        raise ValueError(f"Unknown role '{role_id}'.")

    parsed = resume_parser.parse_resume(resume_bytes, resume_filename)

    record = repository.create_session(
        db,
        role=role_id,
        resume_filename=resume_filename,
        candidate_name=candidate_name,
        extracted_skills=parsed["skills"],
    )
    return {
        "session_id": record.id,
        "role": role_id,
        "extracted_skills": parsed["skills"],
    }


def get_next_question(db: Session, session_id: str) -> dict:
    session = repository.get_session(db, session_id)
    if session is None:
        raise LookupError("Session not found.")
    if session.status == "completed":
        raise PermissionError("This interview session has already been completed.")

    existing_questions = repository.list_questions_for_session(db, session_id)
    total_target = settings.questions_per_interview

    if len(existing_questions) >= total_target:
        raise PermissionError("All questions for this session have already been generated.")

    role = get_role(session.role)
    already_asked_topics = [q.topic for q in existing_questions if q.topic]

    generated = generate_question(
        role_id=session.role,
        role_label=role.label if role else session.role,
        skills=session.extracted_skills or [],
        already_asked_topics=already_asked_topics,
    )

    sequence_number = len(existing_questions) + 1
    question_record = repository.create_question(
        db,
        session_id=session_id,
        question_text=generated["question_text"],
        source_chunk_ids=generated["source_chunk_ids"],
        topic=generated["topic"],
        sequence_number=sequence_number,
    )

    return {
        "question_id": question_record.id,
        "question_text": question_record.question_text,
        "topic": question_record.topic,
        "sequence_number": sequence_number,
        "total_questions": total_target,
        "is_last": sequence_number >= total_target,
    }


def submit_answer(db: Session, *, question_id: str, answer_text: str) -> None:
    question = repository.get_question(db, question_id)
    if question is None:
        raise LookupError("Question not found.")
    if repository.get_answer_for_question(db, question_id) is not None:
        raise ValueError("This question has already been answered.")

    repository.create_answer(db, question_id=question_id, answer_text=answer_text)


def complete_session(db: Session, session_id: str) -> None:
    session = repository.get_session(db, session_id)
    if session is None:
        raise LookupError("Session not found.")
    if session.status == "completed":
        raise ValueError("Session is already completed.")

    repository.complete_session(db, session_id)


def build_summary(db: Session, session_id: str) -> dict:
    session = repository.get_session(db, session_id)
    if session is None:
        raise LookupError("Session not found.")

    questions = repository.list_questions_for_session(db, session_id)
    qa_pairs = []
    topics_covered = set()
    answered_count = 0

    for q in questions:
        answer = repository.get_answer_for_question(db, q.id)
        if answer is not None:
            answered_count += 1
        if q.topic:
            topics_covered.add(q.topic)
        qa_pairs.append({
            "sequence_number": q.sequence_number,
            "question_text": q.question_text,
            "topic": q.topic,
            "answer_text": answer.answer_text if answer else None,
            "source_chunk_ids": q.source_chunk_ids,
        })

    insights = {
        "topics_covered": sorted(topics_covered),
        "total_questions": len(questions),
        "total_answered": answered_count,
        "skills_touched": session.extracted_skills or [],
    }

    return {
        "session": {
            "id": session.id,
            "role": session.role,
            "candidate_name": session.candidate_name,
            "status": session.status,
            "created_at": session.created_at,
        },
        "qa_pairs": qa_pairs,
        "insights": insights,
    }
