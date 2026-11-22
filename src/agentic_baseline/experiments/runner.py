import json
import time

from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from agentic_baseline.agents import (
    build_agent,
    load_agent_config,
)
from agentic_baseline.monitoring.context import RunContext
from agentic_baseline.monitoring.events import EventLogger
from agentic_baseline.monitoring.callbacks import (
    ExperimentCallbackHandler,
)


def _serialize(value: Any) -> Any:
    """Convert Pydantic objects and other values to JSON-compatible data."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")

    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_serialize(item) for item in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return str(value)


def _save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
            default=str,
        )


def _extract_final_answer(response: dict) -> Any:
    """Extract the last AI message without tool calls."""

    messages = response.get("messages", [])

    for message in reversed(messages):
        if (
            isinstance(message, AIMessage)
            and not message.tool_calls
        ):
            return message.content

    return None


async def run_baseline(
    task: str,
    instance_id: str,
) -> dict:

    experiment_id = "baseline"

    # 1. Create run context and output directory.
    context = RunContext.create(
        experiment_id=experiment_id,
        instance_id=instance_id,
    )

    event_logger = EventLogger(
        context.output_dir / "events.jsonl"
    )

    # 2. Load agent configuration.
    agent_config = load_agent_config("general-purpose")

    callback = ExperimentCallbackHandler(
        context=context,
        logger=event_logger,
        agent_id="general-purpose",
        model_name=agent_config.model,
    )

    run_start_ns = time.perf_counter_ns()

    event_logger.log(
        "experiment_start",
        experiment_id=context.experiment_id,
        run_id=context.run_id,
        trace_id=context.trace_id,
        instance_id=context.instance_id,
        agent_id="general-purpose",
        model=agent_config.model,
        task=task,
    )

    try:
        # 3. Build agent.
        build_start_ns = time.perf_counter_ns()

        agent = await build_agent(agent_config)

        build_duration_ms = (
            time.perf_counter_ns() - build_start_ns
        ) / 1_000_000

        # 4. Invoke agent with monitoring callback.
        execution_start_ns = time.perf_counter_ns()

        response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": task,
                    }
                ]
            },
            config={
                "callbacks": [callback],
                "metadata": {
                    "run_id": context.run_id,
                    "trace_id": context.trace_id,
                    "experiment_id": context.experiment_id,
                    "instance_id": context.instance_id,
                    "agent_id": "general-purpose",
                },
            },
        )

        execution_duration_ms = (
            time.perf_counter_ns() - execution_start_ns
        ) / 1_000_000

        # 5. Extract final answer.
        final_answer = _extract_final_answer(response)

        structured_response = response.get(
            "structured_response"
        )

        result_data = {
            "experiment_id": context.experiment_id,
            "run_id": context.run_id,
            "trace_id": context.trace_id,
            "instance_id": context.instance_id,
            "agent_id": "general-purpose",
            "task": task,
            "answer": _serialize(final_answer),
            "structured_response": _serialize(
                structured_response
            ),
        }

        # 6. Collect metrics.
        metrics = callback.get_metrics()

        total_duration_ms = (
            time.perf_counter_ns() - run_start_ns
        ) / 1_000_000

        metrics_data = {
            "experiment_id": context.experiment_id,
            "run_id": context.run_id,
            "trace_id": context.trace_id,
            "instance_id": context.instance_id,
            "agent_id": "general-purpose",
            "model": agent_config.model,
            "agent_build_duration_ms": build_duration_ms,
            "agent_execution_duration_ms": execution_duration_ms,
            "total_duration_ms": total_duration_ms,
            **metrics,
        }

        # 7. Save result and metrics.
        _save_json(
            context.output_dir / "result.json",
            result_data,
        )

        _save_json(
            context.output_dir / "metrics.json",
            metrics_data,
        )

        event_logger.log(
            "experiment_end",
            run_id=context.run_id,
            trace_id=context.trace_id,
            instance_id=context.instance_id,
            agent_id="general-purpose",
            total_duration_ms=total_duration_ms,
            metrics=metrics,
        )

        return {
            "run_id": context.run_id,
            "output_dir": str(context.output_dir),
            "total_duration_ms": total_duration_ms,
            **metrics,
        }

    except Exception as error:
        event_logger.log(
            "experiment_error",
            run_id=context.run_id,
            trace_id=context.trace_id,
            instance_id=context.instance_id,
            agent_id="general-purpose",
            error_type=type(error).__name__,
            error=str(error),
        )

        # Save partial metrics even when the run fails.
        _save_json(
            context.output_dir / "metrics.json",
            {
                "run_id": context.run_id,
                "instance_id": context.instance_id,
                "agent_id": "general-purpose",
                "status": "error",
                "error_type": type(error).__name__,
                "error": str(error),
                **callback.get_metrics(),
            },
        )

        raise