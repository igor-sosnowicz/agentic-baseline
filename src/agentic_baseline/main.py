
import asyncio

from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from agentic_baseline.agents import build_agent


async def main() -> None:
    load_dotenv()

    agent = await build_agent("general-purpose")

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Find LangGraph documentation and then "
                        "open one of found pages and create a short brief "
                        "use its content. Use available tools."
                    ),
                }
            ]
        }
    )

    for message in reversed(response["messages"]):
        if isinstance(message, AIMessage) and not message.tool_calls:
            print(message.text)
            break


if __name__ == "__main__":
    asyncio.run(main())
