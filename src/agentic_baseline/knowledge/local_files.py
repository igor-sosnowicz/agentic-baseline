
import hashlib
from pathlib import Path

from agentic_baseline.knowledge.document_parser import (
    read_text_file,
    SUPPORTED_EXTENSIONS,
)
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS_DIRECTORY = PROJECT_ROOT / "data" / "documents"
DOCUMENT_ID_PATTERN = re.compile(r"^[a-f0-9]{16}$")

def get_document_id(path: Path) -> str:
    """Generate a stable ID based on the relative document path."""
    relative_path = path.resolve().relative_to(
        DOCUMENTS_DIRECTORY.resolve()
    ).as_posix()

    return hashlib.sha256(
        relative_path.encode("utf-8")
    ).hexdigest()[:16]


def search_documents(query: str) -> list[dict[str, str]]:
    """
    Search local documents by filename and content.

    Args:
        query: Text to search for.

    Returns:
        Matching documents with their IDs and paths.
    """
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not DOCUMENTS_DIRECTORY.exists():
        return []

    query = query.casefold()
    results = []

    for path in DOCUMENTS_DIRECTORY.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = read_text_file(path)
        except (OSError, UnicodeError):
            continue

        filename_match = query in path.name.casefold()
        content_match = query in content.casefold()

        if filename_match or content_match:
            results.append(
                {
                    "document_id": get_document_id(path),
                    "name": path.name,
                    "path": path.relative_to(
                        DOCUMENTS_DIRECTORY
                    ).as_posix(),
                }
            )

    return results


def find_document_by_id(document_id: str) -> Path | None:
    """
    Find a document using its stable ID.

    Only documents inside DOCUMENTS_DIRECTORY are considered.
    """
    if not DOCUMENT_ID_PATTERN.fullmatch(document_id):
        return None

    if not DOCUMENTS_DIRECTORY.exists():
        return None

    root = DOCUMENTS_DIRECTORY.resolve()

    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        resolved_path = path.resolve()

        try:
            resolved_path.relative_to(root)
        except ValueError:
            continue

        if get_document_id(resolved_path) == document_id:
            return resolved_path

    return None


def read_document_by_id(document_id: str) -> str:
    """
    Read a document using its document ID.

    Raises:
        FileNotFoundError: If the document does not exist.
    """
    path = find_document_by_id(document_id)

    if path is None:
        raise FileNotFoundError(
            f"Document with ID '{document_id}' was not found."
        )

    return read_text_file(path)