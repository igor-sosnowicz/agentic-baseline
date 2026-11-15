
from pathlib import Path

import pytest

from agentic_baseline.knowledge.local_files import (
    search_documents,
    get_document_id,
    find_document_by_id,
)
from agentic_baseline.knowledge.document_parser import read_text_file


def test_search_documents(monkeypatch, tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    (documents_dir / "example.txt").write_text(
        "LangGraph is a framework for building agents.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    results = search_documents("LangGraph")

    assert len(results) == 1
    assert results[0]["name"] == "example.txt"
    assert results[0]["document_id"]


def test_search_documents_returns_empty_for_no_match(
    monkeypatch, tmp_path
):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    (documents_dir / "example.txt").write_text(
        "Some content",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    assert search_documents("nonexistent") == []


def test_read_text_file(tmp_path):
    document = tmp_path / "example.md"
    document.write_text("# Hello\nTest content", encoding="utf-8")

    assert read_text_file(document) == "# Hello\nTest content"


def test_unsupported_format(tmp_path):
    document = tmp_path / "example.pdf"
    document.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError):
        read_text_file(document)
