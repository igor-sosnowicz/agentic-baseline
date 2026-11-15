
import pytest

from agentic_baseline.knowledge import local_files
from agentic_baseline.tools.documents import (
    read_document,
    search_documents,
)


def test_read_document_tool_invoke(monkeypatch, tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    document = documents_dir / "test.md"
    document.write_text(
        "# LangGraph\n\nTest document content.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        local_files,
        "DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    # Search using the LangChain tool
    search_results = search_documents.invoke(
        {"query": "LangGraph"}
    )

    assert len(search_results) == 1

    document_id = search_results[0]["document_id"]

    # Retrieve using the LangChain tool
    content = read_document.invoke(
        {"document_id": document_id}
    )

    assert content == "# LangGraph\n\nTest document content."


def test_read_document_tool_invalid_id():
    with pytest.raises(FileNotFoundError):
        read_document.invoke(
            {"document_id": "../../.env"}
        )


def test_search_documents_tool_invoke(monkeypatch, tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    (documents_dir / "example.txt").write_text(
        "Artificial intelligence and agents.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        local_files,
        "DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    results = search_documents.invoke(
        {"query": "artificial intelligence"}
    )

    assert len(results) == 1
    assert results[0]["name"] == "example.txt"
    assert results[0]["document_id"]
