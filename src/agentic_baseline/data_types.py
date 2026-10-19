from pathlib import Path
from typing import Literal

from langchain.agents.structured_output import ProviderStrategy
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, HttpUrl


class AgentConfig(BaseModel):
    name: str
    model: str
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
