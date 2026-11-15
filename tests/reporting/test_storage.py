
import json

from agentic_baseline.reporting import storage
from agentic_baseline.reporting.schemas import (
    Report,
    ReportFinding,
    ReportSource,
)


def test_save_report(monkeypatch, tmp_path):
    reports_dir = tmp_path / "reports"

    monkeypatch.setattr(
        storage,
        "REPORTS_DIRECTORY",
        reports_dir,
    )

    report = Report(
        title="Test report",
        summary="Test summary",
        findings=[
            ReportFinding(
                title="Finding 1",
                description="Test description.",
                source_ids=["0123456789abcdef"],
            )
        ],
        sources=[
            ReportSource(document_id="0123456789abcdef")
        ],
    )

    result = storage.save_report(report)

    assert result["status"] == "saved"
    assert result["report_id"]

    file_path = reports_dir / f"{result['report_id']}.json"

    assert file_path.exists()

    with file_path.open(encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data["title"] == "Test report"
    assert saved_data["summary"] == "Test summary"
    assert saved_data["sources"][0]["document_id"] == (
        "0123456789abcdef"
    )


def test_save_report_creates_directory(monkeypatch, tmp_path):
    reports_dir = tmp_path / "new_reports"

    monkeypatch.setattr(
        storage,
        "REPORTS_DIRECTORY",
        reports_dir,
    )

    report = Report(
        title="Report",
        summary="Summary",
        findings=[
            ReportFinding(
                title="Finding",
                description="Description",
            )
        ],
    )

    result = storage.save_report(report)

    assert result["status"] == "saved"
    assert reports_dir.exists()