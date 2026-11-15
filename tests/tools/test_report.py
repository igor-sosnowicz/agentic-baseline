
import pytest

from agentic_baseline.knowledge import local_files
from agentic_baseline.reporting import storage
from agentic_baseline.tools.report import save_report


def test_save_report_tool_invoke(monkeypatch, tmp_path):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    document = documents_dir / "source.txt"
    document.write_text(
        "Information about LangGraph.",
        encoding="utf-8",
    )

    reports_dir = tmp_path / "reports"

    monkeypatch.setattr(
        local_files,
        "DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    monkeypatch.setattr(
        storage,
        "REPORTS_DIRECTORY",
        reports_dir,
    )

    document_id = local_files.get_document_id(document)

    result = save_report.invoke(
        {
            "title": "LangGraph research",
            "summary": "Research about LangGraph.",
            "findings": [
                {
                    "title": "LangGraph framework",
                    "description": "LangGraph supports agent workflows.",
                    "source_ids": [document_id],
                }
            ],
            "sources": [
                {
                    "document_id": document_id,
                }
            ],
        }
    )

    assert result["status"] == "saved"
    assert result["report_id"]

    assert (
        reports_dir / f"{result['report_id']}.json"
    ).exists()


def test_save_report_tool_rejects_unknown_source(
    monkeypatch, tmp_path
):
    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    reports_dir = tmp_path / "reports"

    monkeypatch.setattr(
        local_files,
        "DOCUMENTS_DIRECTORY",
        documents_dir,
    )

    monkeypatch.setattr(
        storage,
        "REPORTS_DIRECTORY",
        reports_dir,
    )

    with pytest.raises(ValueError, match="Source document does not exist"):
        save_report.invoke(
            {
                "title": "Test report",
                "summary": "Test summary",
                "findings": [
                    {
                        "title": "Finding",
                        "description": "Description",
                        "source_ids": ["0123456789abcdef"],
                    }
                ],
                "sources": [
                    {
                        "document_id": "0123456789abcdef",
                    }
                ],
            }
        )

    assert not reports_dir.exists()