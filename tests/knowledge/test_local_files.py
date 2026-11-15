import pytest
from agentic_baseline.knowledge.local_files import (
        read_document_by_id,
        get_document_id
    )

def test_read_document_by_id(monkeypatch, tmp_path):

    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    document = documents_dir / "example.txt"
    document.write_text(
        "This is a test document.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    document_id = get_document_id(document)

    result = read_document_by_id(document_id)

    assert result == "This is a test document."


def test_read_document_by_id_markdown(monkeypatch, tmp_path):
    from agentic_baseline.knowledge.local_files import (
        read_document_by_id,
    )

    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    document = documents_dir / "example.md"
    document.write_text(
        "# Heading\n\nMarkdown content.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    document_id = get_document_id(document)

    assert read_document_by_id(document_id) == (
        "# Heading\n\nMarkdown content."
    )


def test_read_document_by_id_unknown_document(monkeypatch, tmp_path):
    from agentic_baseline.knowledge.local_files import (
        read_document_by_id,
    )

    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    with pytest.raises(FileNotFoundError):
        read_document_by_id("0123456789abcdef")


def test_read_document_by_id_invalid_id(monkeypatch, tmp_path):
    from agentic_baseline.knowledge.local_files import (
        read_document_by_id,
    )

    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    with pytest.raises(FileNotFoundError):
        read_document_by_id("../../.env")


def test_read_document_by_id_nested_directory(monkeypatch, tmp_path):
    from agentic_baseline.knowledge.local_files import (
        read_document_by_id,
    )

    documents_dir = tmp_path / "documents"
    nested_dir = documents_dir / "nested"
    nested_dir.mkdir(parents=True)

    document = nested_dir / "example.txt"
    document.write_text("Nested document.", encoding="utf-8")

    monkeypatch.setattr(
        "agentic_baseline.knowledge.local_files.DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    document_id = get_document_id(document)

    assert read_document_by_id(document_id) == "Nested document."