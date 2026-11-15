
import pytest
from agentic_baseline.agents import build_agent


@pytest.mark.anyio
async def test_researcher_agent_can_be_built():
    agent = await build_agent("researcher")

    assert agent is not None


@pytest.mark.anyio
async def test_researcher_has_document_tools():
    agent = await build_agent("researcher")

    assert agent is not None

    graph = agent.get_graph()
    graph_nodes = graph.nodes

    node_names = set(graph_nodes.keys())

    assert "tools" in node_names
