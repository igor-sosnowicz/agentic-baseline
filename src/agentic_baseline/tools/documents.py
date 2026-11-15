
from langchain.tools import tool

from agentic_baseline.knowledge.local_files import (
    search_documents as search_local_documents,
    read_document_by_id,
)


@tool
def search_documents(query: str) -> list[dict[str, str]]:
    """
    Search local TXT and Markdown documents.

    Args:
        query: Phrase to search for in document names and contents.

    Returns:
        Matching documents with their IDs, names and relative paths.
    """
    return search_local_documents(query)


@tool
def read_document(document_id: str) -> str:
    """
    Read the full contents of a local document using its document ID.

    The document ID must come from search_documents.
    """
    return read_document_by_id(document_id)