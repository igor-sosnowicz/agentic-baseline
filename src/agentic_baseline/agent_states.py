"""
Module with agent states.

Agent state is a typed dictionary that holds the current conversation history and any custom fields your tools and middleware need.
"""

from langchain.agents import AgentState


class GeneralAgentState(AgentState):
    pass

class ResearcherAgentState(AgentState):
    """State for the local document research agent."""

    pass