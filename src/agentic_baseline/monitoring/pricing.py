
from typing import Any

MODEL_PRICING = {
    "gemini-2.5-flash": {
        "input": None,
        "output": None,
        "cache_read": None,
    },
}


def calculate_cost(
    usage: dict[str, Any],
    model: str,
) -> float | None:
    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return None

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    cache_tokens = usage.get("cache_read_tokens")

    if input_tokens is None or output_tokens is None:
        return None

    if pricing["input"] is None or pricing["output"] is None:
        return None

    cache_tokens = cache_tokens or 0
    regular_input = max(0, input_tokens - cache_tokens)

    if cache_tokens and pricing["cache_read"] is None:
        return None

    cost = (
        regular_input * pricing["input"]
        + output_tokens * pricing["output"]
    )

    if cache_tokens:
        cost += cache_tokens * pricing["cache_read"]

    return cost / 1_000_000
