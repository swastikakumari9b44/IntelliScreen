"""
Resume parsing service.

Design choice: rule-based keyword matching against a curated skills
vocabulary, rather than a full NLP/NER model. This is a deliberate
trade-off for this project's scope -- it's deterministic, fast, fully
explainable in an interview, and needs zero extra ML dependencies.
A natural "enhancement" (documented in the README) is swapping this for
spaCy NER or an LLM-based extraction call if more nuance is needed.
"""
import re
from io import BytesIO

from pypdf import PdfReader

# A curated vocabulary covering the roles this system supports. Kept as
# a flat list (not per-role) because a candidate's skills are useful
# context regardless of which role they're interviewing for.
SKILLS_VOCABULARY = [
    "python", "java", "c++", "javascript", "typescript", "sql", "r",
    "machine learning", "deep learning", "neural networks", "nlp",
    "computer vision", "reinforcement learning", "regression",
    "classification", "clustering", "decision trees", "random forest",
    "gradient boosting", "xgboost", "svm", "naive bayes", "pca",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "opencv", "hugging face", "transformers", "llm", "rag",
    "fastapi", "flask", "django", "rest api", "graphql", "microservices",
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "git",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "data structures", "algorithms", "system design", "distributed systems",
    "statistics", "probability", "linear algebra", "data visualization",
    "spark", "hadoop", "airflow", "etl",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_skills(resume_text: str) -> list[str]:
    """
    Matches the resume text (case-insensitively, word-boundary aware)
    against the curated vocabulary. Returns skills in the order they
    appear in the vocabulary (stable, readable output) rather than
    order of appearance in the resume.
    """
    text_lower = resume_text.lower()
    found = []
    for skill in SKILLS_VOCABULARY:
        # \b word boundaries avoid matching "r" inside "react", etc.
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return found


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """
    Top-level entry point used by the API layer.
    Raises ValueError on unsupported file types or unreadable content --
    the API layer translates this into a clean 400/422 response.
    """
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF resumes are currently supported.")

    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("Could not extract any text from the uploaded PDF.")

    skills = extract_skills(text)
    return {"raw_text": text, "skills": skills}
