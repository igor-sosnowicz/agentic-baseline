
from mcp.server.fastmcp import FastMCP

from agentic_baseline.data_types import Website
from agentic_baseline.tools.find_websites import find_websites_tool
from agentic_baseline.tools.access_website import access_website_tool

mcp = FastMCP("agentic-baseline-tools")


@mcp.tool()
def find_websites(query: str) -> list[dict]:
    """Search for websites matching a query."""
    results = find_websites_tool(query=query)

    websites = [
        Website(
            url=result["href"],
            title=result["title"],
            description=result.get("body", ""),
        )
        for result in results
    ]

    return [
        website.model_dump(mode="json")
        for website in websites
    ]


@mcp.tool()
def access_website(url: str) -> str:
    """Fetch website content formatted as Markdown."""
    return access_website_tool(url=url)


if __name__ == "__main__":
    mcp.run()