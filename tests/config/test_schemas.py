
import pytest
from pydantic import ValidationError

from agentic_baseline.config.schemas import ExperimentsConfig


def test_valid_configuration():
    config = ExperimentsConfig.model_validate({
        "active_experiment": "baseline",
        "experiments": {
            "baseline": {
                "decomposition": "none",
                "delegation": "disabled",
                "agents": ["general_purpose"]
            },
            "high_level": {
                "decomposition": "high",
                "delegation": "disabled",
                "agents": ["researcher"]
            },
            "low_level": {
                "decomposition": "low",
                "delegation": "explicit",
                "agents": ["researcher"],
                "subagents": {
                    "researcher": ["document_search"]
                }
            }
        }
    })

    assert config.active_experiment == "baseline"


def test_missing_experiments_field():
    with pytest.raises(ValidationError):
        ExperimentsConfig.model_validate({})


def test_experiments_must_be_mapping():
    with pytest.raises(ValidationError):
        ExperimentsConfig.model_validate({
            "experiments": []
        })