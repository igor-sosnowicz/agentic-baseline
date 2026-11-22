
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from agentic_baseline.reporting.schemas import (
    Report,
    ReportFinding,
    ReportArgument,
    ArgumentRelation,
    ReportSource,
)
from agentic_baseline.reporting.storage import save_report as store_report
from agentic_baseline.knowledge.local_files import find_document_by_id


class ReportToolInput(BaseModel):
    title: str = Field(description="Report title")
    summary: str = Field(description="Report summary")

    findings: list[ReportFinding] = Field(
        default_factory=list,
        description="General research findings, when applicable",
    )
    arguments: list[ReportArgument] = Field(
        default_factory=list,
        description="Identified arguments, when the task involves argument analysis",
    )
    relations: list[ArgumentRelation] = Field(
        default_factory=list,
        description="Relationships between identified arguments",
    )
    sources: list[ReportSource] = Field(
        default_factory=list,
        description="Documents used as report sources",
    )


@tool(args_schema=ReportToolInput)
def save_report(
    title: str,
    summary: str,
    findings: list[ReportFinding] | None = None,
    arguments: list[ReportArgument] | None = None,
    relations: list[ArgumentRelation] | None = None,
    sources: list[ReportSource] | None = None,
) -> dict[str, str]:
    """
    Validate and save a research report as a JSON file.

    Every declared source must reference an existing local document.
    Returns a confirmation with the generated report ID.
    """
    report = Report(
        title=title,
        summary=summary,
        findings=findings or [],
        arguments=arguments or [],
        relations=relations or [],
        sources=sources or [],
    )

    for source in report.sources:
        if find_document_by_id(source.document_id) is None:
            raise ValueError(
                f"Source document does not exist: {source.document_id}"
            )

    return store_report(report)