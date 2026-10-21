import importlib
from typing import cast

import yaml
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware.types import InputAgentState, OutputAgentState
from langchain.tools import BaseTool
from langchain_openrouter import ChatOpenRouter
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from agentic_baseline.constants import AGENTS_CONFIGURATION_DIRECTORY
from agentic_baseline.data_types import AgentConfig


def build_agent(
    agent_config: AgentConfig | str,
) -> CompiledStateGraph[
    AgentState[BaseModel],
    None,
    InputAgentState,
    OutputAgentState[BaseModel],
]:
    """
    Build an agent.

    Args:
        agent_config (AgentConfig | str): Either a agent configuration DTO or
            filename of agent configuration without a file extension (e.g. ".yaml").

    Returns:
        CompiledStateGraph: An AI agent constructed according to the configuration.
    """
    if isinstance(agent_config, str):
        agent_config = _parse_yaml_agent_config_file(config_filename=agent_config)

    reasoning = (
        {"effort": agent_config.reasoning_effort}
        if agent_config.reasoning_effort is not None
        else None
    )

    model = ChatOpenRouter(
        model=agent_config.model,
        reasoning=reasoning,
    )

    return create_agent(
        model=model,
        tools=agent_config.tools,
        state_schema=agent_config.agent_state,
        system_prompt=agent_config.get_system_prompt(),
        response_format=agent_config.response_format,
    )


def _parse_yaml_agent_config_file(config_filename: str) -> AgentConfig:

    with open(AGENTS_CONFIGURATION_DIRECTORY / f"{config_filename}.yaml") as file:
        data = yaml.safe_load(file)

        data["tools"] = [
            _resolve_tool_by_name(tool_name) for tool_name in data["tools"]
        ]
        data["agent_state"] = _resolve_agent_state_by_name(data["agent_state"])

        return AgentConfig(**data)


def _load_from_module(
    module_name: str,
    name: str,
    entity_kind: str,
    expected_type: type | None = None,
) -> object:
    """Load an attribute by name from a module, optionally validating its type."""
    try:
        module = importlib.import_module(module_name)
        attr = getattr(module, name)
        if expected_type is not None and not isinstance(attr, expected_type):
            raise TypeError(f"{name} is not a {entity_kind}.")
        return attr
    except ImportError:
        raise ImportError(f"Module '{module_name}' not found.")
    except AttributeError:
        raise AttributeError(
            f"{entity_kind} '{name}' not found in module '{module_name}'."
        )


def _resolve_agent_state_by_name(agent_state_name: str) -> type[AgentState]:
    return cast(
        "type[AgentState]",
        _load_from_module(
            module_name="agentic_baseline.agent_states",
            name=agent_state_name,
            entity_kind="class",
            expected_type=type,
        ),
    )


def _resolve_tool_by_name(tool_name: str) -> BaseTool:
    return cast(
        "BaseTool",
        _load_from_module(
            module_name="agentic_baseline.tools.api",
            name=tool_name,
            entity_kind="tool",
            expected_type=BaseTool,
        ),
    )
