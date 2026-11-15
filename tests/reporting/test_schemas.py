
import pytest
from pydantic import ValidationError

from agentic_baseline.reporting.schemas import (
    Report,
    ReportFinding,
    ReportSource,
)


def test_valid_report():
    report = Report(
        title="Research report",
        summary="A summary of the research.",
        findings=[
            ReportFinding(
                title="Finding 1",
                description="Important information.",
                source_ids=["0123456789abcdef"],
            )
        ],
        sources=[
            ReportSource(document_id="0123456789abcdef")
        ],
    )

    assert report.title == "Research report"
    assert len(report.findings) == 1
    assert len(report.sources) == 1
    assert report.created_at is not None


def test_report_rejects_empty_title():
    with pytest.raises(ValidationError):
        Report(
            title="",
            summary="Summary",
            findings=[
                ReportFinding(
                    title="Finding",
                    description="Description",
                )
            ],
        )


def test_report_rejects_duplicate_sources():
    with pytest.raises(ValidationError):
        Report(
            title="Report",
            summary="Summary",
            findings=[
                ReportFinding(
                    title="Finding",
                    description="Description",
                )
            ],
            sources=[
                ReportSource(document_id="0123456789abcdef"),
                ReportSource(document_id="0123456789abcdef"),
            ],
        )


def test_report_rejects_unknown_finding_source():
    with pytest.raises(ValidationError):
        Report(
            title="Report",
            summary="Summary",
            findings=[
                ReportFinding(
                    title="Finding",
                    description="Description",
                    source_ids=["aaaaaaaaaaaaaaaa"],
                )
            ],
            sources=[
                ReportSource(document_id="0123456789abcdef")
            ],
        )


def test_report_rejects_invalid_document_id():
    with pytest.raises(ValidationError):
        ReportSource(document_id="../../.env")