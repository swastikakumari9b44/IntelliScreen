"""
Role -> Knowledge Base mapping.

This is the single source of truth for which roles the system supports
and which provided textbook(s) back each role's Retrieval-Augmented
Generation pipeline. Both the ingestion script and the retrieval service
import this file, so there is exactly one place to add/change a role.

Per the assignment (Section 9), only the provided books are used as the
RAG knowledge source -- no generic internet content.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleDefinition:
    id: str
    label: str
    collection_name: str          # ChromaDB collection for this role
    source_files: tuple[str, ...] # PDF filenames expected in data/knowledge_base/
    description: str


ROLES: dict[str, RoleDefinition] = {
    "ml_engineer": RoleDefinition(
        id="ml_engineer",
        label="Machine Learning Engineer",
        collection_name="kb_ml_engineer",
        source_files=(
            "machine_learning_tom_mitchell.pdf",
            "hundred_page_ml_book.pdf",
            "ml_for_absolute_beginners.pdf",
        ),
        description="Core ML concepts, algorithms, and fundamentals.",
    ),
    "data_scientist": RoleDefinition(
        id="data_scientist",
        label="Data Scientist / Applied ML",
        collection_name="kb_data_scientist",
        source_files=(
            "intro_to_ml_with_python.pdf",
            "master_ml_algorithms_brownlee.pdf",
        ),
        description="Applied ML workflows, practical algorithm usage.",
    ),
    "ai_engineer": RoleDefinition(
        id="ai_engineer",
        label="AI Engineer",
        collection_name="kb_ai_engineer",
        source_files=(
            "ai_ml_deep_learning.pdf",
        ),
        description="Broad AI/ML/DL systems and concepts.",
    ),
    "advanced_ml": RoleDefinition(
        id="advanced_ml",
        label="Advanced ML (Research / Theory)",
        collection_name="kb_advanced_ml",
        source_files=(
            "pattern_recognition_bishop.pdf",
        ),
        description="Theoretical/statistical ML for strong candidates.",
    ),
}


def get_role(role_id: str) -> RoleDefinition | None:
    return ROLES.get(role_id)


def list_roles() -> list[RoleDefinition]:
    return list(ROLES.values())
