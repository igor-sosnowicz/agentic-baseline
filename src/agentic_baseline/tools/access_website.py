"""An implementation of the `access_website` tool for agents."""

from ddgs import DDGS

from agentic_baseline.constants import WEBSITE_ACCESS_TIMEOUT


def access_website_tool(url: str) -> str:
    # TODO: Validate URL.
    result = DDGS(
        timeout=WEBSITE_ACCESS_TIMEOUT.total_seconds()
    ).extract(url, fmt="text_markdown")

    if isinstance(result, dict):
        return result.get("content", str(result))

    return str(result)
