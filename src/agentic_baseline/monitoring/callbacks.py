import time
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler

from agentic_baseline.monitoring.context import RunContext
from agentic_baseline.monitoring.events import EventLogger
from agentic_baseline.monitoring.pricing import calculate_cost


def extract_usage(response: Any) -> dict:
    usage = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cache_read_tokens": None,
        "reasoning_tokens": None,
    }

    for generation_list in getattr(response, "generations", []):
        for generation in generation_list:
            message = getattr(generation, "message", None)

            if message is None:
                continue

            metadata = getattr(message, "usage_metadata", None) or {}
            response_metadata = (
                getattr(message, "response_metadata", None) or {}
            )

            token_usage = (
                response_metadata.get("token_usage")
                or response_metadata.get("usage")
                or {}
            )

            usage["input_tokens"] = (
                metadata.get("input_tokens")
                if metadata.get("input_tokens") is not None
                else token_usage.get("prompt_tokens")
            )

            usage["output_tokens"] = (
                metadata.get("output_tokens")
                if metadata.get("output_tokens") is not None
                else token_usage.get("completion_tokens")
            )

            usage["total_tokens"] = (
                metadata.get("total_tokens")
                if metadata.get("total_tokens") is not None
                else token_usage.get("total_tokens")
            )

            input_details = metadata.get("input_token_details") or {}
            output_details = metadata.get("output_token_details") or {}

            usage["cache_read_tokens"] = (
                input_details.get("cache_read")
                or input_details.get("cache_read_tokens")
                or token_usage.get("cached_tokens")
            )

            usage["reasoning_tokens"] = (
                output_details.get("reasoning")
                or output_details.get("reasoning_tokens")
                or token_usage.get("reasoning_tokens")
            )

            return usage

    return usage


class ExperimentCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        context: RunContext,
        logger: EventLogger,
        agent_id: str,
        model_name: str
    ):
        self.context = context
        self.logger = logger
        self.agent_id = agent_id

        self.started = {}
        self.model_names = {}
        self.tool_names = {}

        self.model_calls = 0
        self.tool_calls = 0

        self.model_name = model_name
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_tokens = 0
        self.total_reasoning_tokens = 0

        self.known_input_tokens = 0
        self.known_output_tokens = 0
        self.known_cache_tokens = 0
        self.known_reasoning_tokens = 0

        self.total_cost_usd = 0.0
        self.cost_is_complete = True

    def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        self.model_calls += 1
        self.started[run_id] = time.perf_counter_ns()

        self.logger.log(
            "model_start",
            run_id=self.context.run_id,
            trace_id=self.context.trace_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            parent_run_id=str(parent_run_id) if parent_run_id else None,
            model=(serialized or {}).get("name"),
            prompts=prompts,
        )

    def on_llm_end(
        self,
        response,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        start = self.started.pop(run_id, None)

        duration_ms = (
            (time.perf_counter_ns() - start) / 1_000_000
            if start is not None
            else None
        )

        usage, cost = self.record_usage(response)

        self.logger.log(
            "model_end",
            run_id=self.context.run_id,
            trace_id=self.context.trace_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            parent_run_id=(
                str(parent_run_id) if parent_run_id else None
            ),
            usage=usage,
            cost=cost,
            generations=str(response.generations),
            duration_ms=duration_ms,
        )

    def on_llm_error(
        self,
        error,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        start = self.started.pop(run_id, None)

        self.logger.log(
            "model_error",
            run_id=self.context.run_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            error_type=type(error).__name__,
            error=str(error),
            duration_ms=(
                (time.perf_counter_ns() - start) / 1_000_000
                if start is not None
                else None
            ),
        )

    def on_tool_start(
        self,
        serialized,
        input_str,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        self.tool_calls += 1
        self.started[run_id] = time.perf_counter_ns()

        tool_name = (serialized or {}).get("name", "unknown")

        self.logger.log(
            "tool_start",
            run_id=self.context.run_id,
            trace_id=self.context.trace_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            parent_run_id=str(parent_run_id) if parent_run_id else None,
            tool_name=tool_name,
            arguments=input_str,
        )

    def on_tool_end(
        self,
        output,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        start = self.started.pop(run_id, None)

        self.logger.log(
            "tool_end",
            run_id=self.context.run_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            output=str(output),
            duration_ms=(
                (time.perf_counter_ns() - start) / 1_000_000
                if start is not None
                else None
            ),
        )

    def on_tool_error(
        self,
        error,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        start = self.started.pop(run_id, None)

        self.logger.log(
            "tool_error",
            run_id=self.context.run_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            error_type=type(error).__name__,
            error=str(error),
            duration_ms=(
                (time.perf_counter_ns() - start) / 1_000_000
                if start is not None
                else None
            ),
        )
    # for test purposes
    def on_chat_model_start(
        self,
        serialized,
        messages,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        self.model_calls += 1
        self.started[run_id] = time.perf_counter_ns()

        self.logger.log(
            "model_start",
            run_id=self.context.run_id,
            trace_id=self.context.trace_id,
            agent_id=self.agent_id,
            callback_run_id=str(run_id),
            parent_run_id=(
                str(parent_run_id)
                if parent_run_id
                else None
            ),
            model=(serialized or {}).get("name"),
            messages=str(messages),
        )

    def record_usage(self, response):
        usage = extract_usage(response)

        input_tokens = usage["input_tokens"]
        output_tokens = usage["output_tokens"]
        cache_tokens = usage["cache_read_tokens"]
        reasoning_tokens = usage["reasoning_tokens"]

        if input_tokens is not None:
            self.total_input_tokens += input_tokens
            self.known_input_tokens += 1

        if output_tokens is not None:
            self.total_output_tokens += output_tokens
            self.known_output_tokens += 1

        if cache_tokens is not None:
            self.total_cache_tokens += cache_tokens
            self.known_cache_tokens += 1

        if reasoning_tokens is not None:
            self.total_reasoning_tokens += reasoning_tokens
            self.known_reasoning_tokens += 1

        cost = calculate_cost(
            usage=usage,
            model=self.model_name,
        )

        if cost is None:
            self.cost_is_complete = False
        else:
            self.total_cost_usd += cost

        return usage, cost

    def get_metrics(self) -> dict:
        return {
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,

            "input_tokens": (
                self.total_input_tokens
                if self.known_input_tokens == self.model_calls
                else None
            ),

            "output_tokens": (
                self.total_output_tokens
                if self.known_output_tokens == self.model_calls
                else None
            ),

            "cache_read_tokens": (
                self.total_cache_tokens
                if self.known_cache_tokens == self.model_calls
                else None
            ),

            "reasoning_tokens": (
                self.total_reasoning_tokens
                if self.known_reasoning_tokens == self.model_calls
                else None
            ),

            "total_cost_usd": (
                self.total_cost_usd
                if self.cost_is_complete and self.model_calls > 0
                else None
            ),
        }