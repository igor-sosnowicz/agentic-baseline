
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ConfigDict, model_validator


class ReportSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(
        min_length=16,
        max_length=16,
        pattern=r"^[a-f0-9]{16}$",
        description="ID document returned by search_documents",
    )


class ReportFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_ids: list[str] = Field(default_factory=list)


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1)
    findings: list[ReportFinding] = Field(min_length=1)
    sources: list[ReportSource] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @model_validator(mode="after")
    def validate_sources(self):
        source_ids = [source.document_id for source in self.sources]

        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Duplicate document IDs in report sources.")

        available_ids = set(source_ids)

        for finding in self.findings:
            missing_ids = set(finding.source_ids) - available_ids

            if missing_ids:
                raise ValueError(
                    f"Finding references unknown sources: {missing_ids}"
                )

        return self