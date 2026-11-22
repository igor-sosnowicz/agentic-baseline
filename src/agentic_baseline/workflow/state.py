
import operator
from typing import Annotated, Any, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state for the multi-agent workflow.

    The state is shared between workflow nodes, but each agent
    should receive only the fields required for its task.
    """

    run_id: str
    experiment_name: str
    task: str

    # Researcher output
    found_documents: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    research_results: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    # Analysis output
    analysis_results: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    # Future low-level decomposition
    claims: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    evidence: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    argument_candidates: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    argument_pairs: Annotated[
        list[dict[str, Any]],
        operator.add,
    ]

    final_report: dict[str, Any]
    report_answer: str

    errors: Annotated[list[str], operator.add]
    status: str