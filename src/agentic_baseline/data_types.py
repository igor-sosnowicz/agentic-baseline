from pathlib import Path
from typing import Literal

from langchain.agents.structured_output import ProviderStrategy
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, HttpUrl
from enum import StrEnum


class AgentConfig(BaseModel):
    name: str
    model: str
    model_provider: str
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high", "xhigh"]
    tools: list[BaseTool]
    system_prompt_path: Path
    agent_state: type  # Actually type[AgentState] but Pydantic fails to validate it.
    # For structured output. For example: response_format=ProviderStrategy(YourPydanticModel).
    response_format: ProviderStrategy[BaseModel] | None = None

    def get_system_prompt(self) -> str:
        return self.system_prompt_path.read_text(encoding="utf-8")


class Website(BaseModel):
    url: HttpUrl = Field(..., description="HTTP URL to a website.")
    title: str = Field(..., description="The title of a website.")
    description: str = Field(
        ..., description="A short summary of page website or its content's preview."
    )

class InterpretativeFrame(StrEnum):
    """Universal interpretative frames from the Policy Frames Codebook."""

    ECONOMIC = "Economic"
    CAPACITY_AND_RESOURCES = "Capacity and Resources"
    MORALITY = "Morality"
    FAIRNESS_AND_EQUALITY = "Fairness and Equality"
    CONSTITUTIONALITY_AND_LEGALITY = "Constitutionality and Legality"
    POLICY_PRESCRIPTION = "Policy Prescription and Evaluation"
    CRIME_AND_JUSTICE = "Crime and Justice"
    SECURITY_AND_DEFENSE = "Security and Defense"
    HEALTH_AND_SAFETY = "Health and Safety"
    QUALITY_OF_LIFE = "Quality of Life"
    CULTURAL_IDENTITY = "Cultural Identity"
    PUBLIC_OPINION = "Public Opinion"
    POLITICAL = "Political"
    EXTERNAL_REGULATION = "External Regulation and Reputation"
    OTHER = "Other"

class ArgumentAnalysis(BaseModel):
    claim: str
    evidence: list[str]
    style: str

class ArgumentAnalysisWithFrame(ArgumentAnalysis):
    interpretative_frame: InterpretativeFrame

class ArgumentAnalysisResult(BaseModel):
    arguments: list[ArgumentAnalysis]
