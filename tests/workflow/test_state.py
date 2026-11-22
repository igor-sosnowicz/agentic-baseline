
from typing import get_type_hints, get_args, get_origin, Annotated
import operator

from agentic_baseline.workflow.state import AgentState


def test_agent_state_contains_required_fields():
    hints = get_type_hints(AgentState, include_extras=True)

    required_fields = {
        "run_id",
        "experiment_name",
        "task",
        "found_documents",
        "research_results",
        "analysis_results",
        "final_report",
        "report_answer",
        "errors",
        "status",
    }

    assert required_fields.issubset(hints.keys())


def test_agent_state_supports_low_level_fields():
    hints = get_type_hints(AgentState, include_extras=True)

    assert "claims" in hints
    assert "evidence" in hints
    assert "argument_candidates" in hints
    assert "argument_pairs" in hints


def test_parallel_results_can_be_merged():
    first_result = [
        {"claim": "Claim A"}
    ]

    second_result = [
        {"claim": "Claim B"}
    ]

    merged = operator.add(first_result, second_result)

    assert len(merged) == 2
    assert merged[0]["claim"] == "Claim A"
    assert merged[1]["claim"] == "Claim B"


def test_list_fields_use_add_reducer():
    hints = get_type_hints(AgentState, include_extras=True)

    for field in (
        "found_documents",
        "research_results",
        "analysis_results",
        "claims",
        "evidence",
        "argument_candidates",
        "argument_pairs",
        "errors",
    ):
        field_type = hints[field]

        assert get_origin(field_type) is Annotated

        metadata = get_args(field_type)[1:]

        assert operator.add in metadata