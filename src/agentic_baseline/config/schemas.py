
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class DecompositionLevel(StrEnum):
    NONE = "none"
    HIGH = "high"
    LOW = "low"


class DelegationMode(StrEnum):
    DISABLED = "disabled"
    EXPLICIT = "explicit"


class ExecutionMode(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class ExperimentConfig(BaseModel):
    decomposition: DecompositionLevel
    delegation: DelegationMode
    execution: ExecutionMode = ExecutionMode.SEQUENTIAL

    agents: list[str] = Field(min_length=1)
    subagents: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_decomposition(self):
        if self.decomposition == DecompositionLevel.NONE:
            if self.delegation != DelegationMode.DISABLED:
                raise ValueError(
                    "Baseline cannot use delegation."
                )

            if self.agents != ["general_purpose"]:
                raise ValueError(
                    "Baseline must use only general_purpose."
                )

            if self.subagents:
                raise ValueError(
                    "Baseline cannot define subagents."
                )

        elif self.decomposition == DecompositionLevel.HIGH:
            if self.delegation != DelegationMode.DISABLED:
                raise ValueError(
                    "High-level decomposition does not use delegation."
                )

            if self.subagents:
                raise ValueError(
                    "High-level decomposition cannot define subagents."
                )

        elif self.decomposition == DecompositionLevel.LOW:
            if self.delegation != DelegationMode.EXPLICIT:
                raise ValueError(
                    "Low-level decomposition requires explicit delegation."
                )

        return self


class ExperimentsConfig(BaseModel):
    active_experiment: str
    experiments: dict[str, ExperimentConfig]

    @model_validator(mode="after")
    def validate_active_experiment(self):
        if self.active_experiment not in self.experiments:
            raise ValueError(
                f"Unknown experiment: {self.active_experiment}"
            )

        return self