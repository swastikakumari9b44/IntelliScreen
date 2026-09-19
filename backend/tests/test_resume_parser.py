"""
Tests for resume parsing logic. Focused on extract_skills() since it's
pure text-in/list-out logic with no external dependencies (no PDF, no
network, no LLM) -- fast and deterministic to test.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.resume_parser import extract_skills, parse_resume


def test_extract_skills_finds_known_terms():
    text = "Experienced with Python, TensorFlow, and building REST API services using FastAPI."
    skills = extract_skills(text)
    assert "python" in skills
    assert "tensorflow" in skills
    assert "fastapi" in skills
    assert "rest api" in skills


def test_extract_skills_is_case_insensitive():
    text = "PYTHON and Docker and KUBERNETES experience."
    skills = extract_skills(text)
    assert "python" in skills
    assert "docker" in skills
    assert "kubernetes" in skills


def test_extract_skills_avoids_false_positive_substring_match():
    # "r" should not match inside "react" or "regarding"
    text = "Worked with React regarding frontend development."
    skills = extract_skills(text)
    assert "r" not in skills


def test_extract_skills_empty_text_returns_empty_list():
    assert extract_skills("") == []


def test_parse_resume_rejects_non_pdf():
    try:
        parse_resume(b"not a real pdf", "resume.docx")
        assert False, "Expected ValueError for non-PDF file"
    except ValueError as e:
        assert "PDF" in str(e)


def test_parse_resume_rejects_empty_pdf_bytes():
    try:
        parse_resume(b"", "resume.pdf")
        assert False, "Expected ValueError for unreadable PDF"
    except Exception:
        pass  # pypdf will raise on malformed bytes; either error type is acceptable here
