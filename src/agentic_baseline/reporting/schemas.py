
from datetime import datetime, timezone
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class RelationType(StrEnum):
    """Types of relationships between arguments."""

    COUNTERARGUES = "counterargues"
    SUPPORTS = "supports"
    QUALIFIES = "qualifies"
    CONTRADICTS = "contradicts"
    RELATED_TO = "related_to"


class ReportSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(
        min_length=16,
        max_length=16,
        pattern=r"^[a-f0-9]{16}$",
        description="ID document returned by search_documents",
    )


class ReportFinding(BaseModel):
    """A general research finding, not necessarily an argument."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source_ids: list[str] = Field(default_factory=list)


class ReportArgument(BaseModel):
    """A single argument identified in the source material."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        min_length=1,
        description="Unique argument ID within this report, e.g. A1",
    )
    claim: str = Field(
        min_length=1,
        description="The central claim of the argument",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Evidence supporting or illustrating the claim",
    )
    style: str = Field(
        min_length=1,
        description="The rhetorical style of the argument",
    )
    source_ids: list[str] = Field(
        default_factory=list,
        description="IDs of source documents supporting this argument",
    )


class ArgumentRelation(BaseModel):
    """A directed relationship between two identified arguments."""

    model_config = ConfigDict(extra="forbid")

    source_argument_id: str = Field(
        description="ID of the argument establishing the relationship",
    )
    target_argument_id: str = Field(
        description="ID of the argument the relationship refers to",
    )
    type: RelationType
    explanation: str = Field(
        min_length=1,
        description="Explanation of why this relationship exists",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional model-estimated confidence, from 0 to 1",
    )


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1)

    findings: list[ReportFinding] = Field(default_factory=list)
    arguments: list[ReportArgument] = Field(default_factory=list)
    relations: list[ArgumentRelation] = Field(default_factory=list)

    sources: list[ReportSource] = Field(default_factory=list)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @model_validator(mode="after")
    def validate_report(self):
        if not self.findings and not self.arguments:
            raise ValueError(
                "A report must contain at least one finding or argument."
            )

        source_ids = [source.document_id for source in self.sources]

        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Duplicate document IDs in report sources.")

        available_source_ids = set(source_ids)

        for item in [*self.findings, *self.arguments]:
            missing_ids = set(item.source_ids) - available_source_ids

            if missing_ids:
                raise ValueError(
                    f"Item references unknown sources: {missing_ids}"
                )

        argument_ids = [argument.id for argument in self.arguments]

        if len(argument_ids) != len(set(argument_ids)):
            raise ValueError("Duplicate argument IDs in report.")

        available_argument_ids = set(argument_ids)
        relation_keys = set()

        for relation in self.relations:
            if relation.source_argument_id == relation.target_argument_id:
                raise ValueError(
                    "An argument cannot have a relationship with itself."
                )

            if relation.source_argument_id not in available_argument_ids:
                raise ValueError(
                    f"Unknown source argument: {relation.source_argument_id}"
                )

            if relation.target_argument_id not in available_argument_ids:
                raise ValueError(
                    f"Unknown target argument: {relation.target_argument_id}"
                )

            key = (
                relation.source_argument_id,
                relation.target_argument_id,
                relation.type,
            )

            if key in relation_keys:
                raise ValueError("Duplicate argument relationship.")

            relation_keys.add(key)

        return self