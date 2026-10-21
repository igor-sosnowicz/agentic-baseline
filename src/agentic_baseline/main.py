from dotenv import load_dotenv
from langchain_core.messages import AIMessage

from agentic_baseline.agents import build_agent


def main() -> None:
    load_dotenv()  # Load API keys from `.env`.
    agent = build_agent("general-purpose")
    response = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "What's the weather in Wrocław in Poland?"}
            ]
        }
    )

    final_message = next(
        message
        for message in reversed(response["messages"])
        if isinstance(message, AIMessage) and not message.tool_calls
    )

    print(final_message.text)


if __name__ == "__main__":
    main()
