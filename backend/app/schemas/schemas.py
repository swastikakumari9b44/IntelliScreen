"""
Pydantic request/response models.

Why: FastAPI uses these for automatic request validation (satisfies the
assignment's "robust validation" expectation) and for generating the
Swagger/OpenAPI docs, which double as a good demo artifact.
"""
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- Roles ----------

class RoleOut(BaseModel):
    id: str
    label: str
    description: str


# ---------- Sessions ----------

class SessionCreateResponse(BaseModel):
    session_id: str
    role: str
    extracted_skills: list[str]


class SessionSummaryOut(BaseModel):
    id: str
    role: str
    candidate_name: str | None
    status: str
    created_at: datetime


# ---------- Questions / Answers ----------

class NextQuestionOut(BaseModel):
    question_id: str
    question_text: str
    topic: str | None
    sequence_number: int
    total_questions: int
    is_last: bool


class AnswerIn(BaseModel):
    question_id: str
    answer_text: str = Field(..., min_length=1, max_length=5000)


class AnswerAck(BaseModel):
    status: str = "recorded"


class CompleteAck(BaseModel):
    status: str = "completed"


class QAPair(BaseModel):
    sequence_number: int
    question_text: str
    topic: str | None
    answer_text: str | None
    source_chunk_ids: list[str]


class InsightsOut(BaseModel):
    topics_covered: list[str]
    total_questions: int
    total_answered: int
    skills_touched: list[str]


class SessionDetailOut(BaseModel):
    session: SessionSummaryOut
    qa_pairs: list[QAPair]
    insights: InsightsOut
