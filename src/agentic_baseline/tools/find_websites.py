"""An implementation of the `find_website` tool for agents."""

from ddgs import DDGS

from agentic_baseline.constants import WEBSITE_ACCESS_TIMEOUT
from agentic_baseline.data_types import Website


def find_websites_tool(query: str) -> list[Website]:
    return DDGS(timeout=WEBSITE_ACCESS_TIMEOUT.total_seconds()).text(
        query=query,
        # region="us-en",
        # safesearch: str = "moderate",
        # timelimit: str | None = None,
        # max_results: int | None = 10,
        # page: int = 1,
        # backend: str = "auto"
    )
