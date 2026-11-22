import argparse
import asyncio

from dotenv import load_dotenv
from loguru import logger

from agentic_baseline.experiments.runner import run_baseline #only baseline for now


async def async_main(args):
    load_dotenv()

    result = await run_baseline(
        task=args.task,
        instance_id=args.instance,
    )

    logger.info(
        "Experiment completed: {}",
        result["run_id"],
    )

    logger.info(
        "Duration: {} ms",
        result["total_duration_ms"],
    )

    logger.info(
        "Model calls: {}",
        result["model_calls"],
    )

    logger.info(
        "Tool calls: {}",
        result["tool_calls"],
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--experiment",
        default="baseline",
        choices=["baseline"],
    )

    parser.add_argument(
        "--instance",
        required=True,
    )

    parser.add_argument(
        "--task",
        required=True,
    )

    args = parser.parse_args()

    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
