"""
ORM models.

Three tables, matching exactly what the assignment asks the system to
persist: session data, questions asked, and answers given.

Relationships:
  Session (1) --> (N) Question   -- one interview has many questions
  Question (1) --> (1) Answer    -- each question has at most one answer

`source_chunk_ids` on Question is the traceability field the assignment
explicitly calls for ("Ensure traceability of how questions were
generated") -- it stores which retrieved knowledge-base chunks produced
that question.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class SessionRecord(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=_uuid)
    candidate_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    resume_filename = Column(String, nullable=False)
    extracted_skills = Column(JSON, nullable=True)  # list[str] snapshot from resume parse
    status = Column(String, nullable=False, default="in_progress")  # in_progress | completed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    questions = relationship(
        "QuestionRecord", back_populates="session", cascade="all, delete-orphan"
    )


class QuestionRecord(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    source_chunk_ids = Column(JSON, nullable=False, default=list)  # traceability
    topic = Column(String, nullable=True)
    sequence_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionRecord", back_populates="questions")
    answer = relationship(
        "AnswerRecord", back_populates="question", uselist=False, cascade="all, delete-orphan"
    )


class AnswerRecord(Base):
    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=_uuid)
    question_id = Column(
        String, ForeignKey("questions.id"), nullable=False, unique=True, index=True
    )
    answer_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("QuestionRecord", back_populates="answer")
