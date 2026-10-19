from langchain.tools import tool

from agentic_baseline.data_types import Website
from agentic_baseline.tools.access_website import access_website_tool
from agentic_baseline.tools.find_websites import find_websites_tool


# Mandatory docstring because they're used by agents.
@tool
def find_websites(query: str) -> list[Website]:
    """
    Perform a web search to find websites related to `query`.

    Args:
        query (str): Search query for an Internet search engine.

    Returns:
        list[Website]: List of matching websites.
    """
    return find_websites_tool(query=query)


@tool
def access_website(url: str) -> str:
    """
    Access content of a website.

    Args:
        url (str): An URL of an HTTP website.

    Returns:
        str: Content of the website formatted with Markdown.
    """
    return access_website_tool(url=url)


__all__ = [
    "access_website",
    "find_websites",
]
