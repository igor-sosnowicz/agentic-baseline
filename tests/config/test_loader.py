
import pytest

from agentic_baseline.config.loader import (
    load_config,
    get_experiment,
)


VALID_YAML = """
active_experiment: baseline

experiments:
  baseline:
    decomposition: none
    delegation: disabled
    execution: sequential
    agents:
      - general_purpose

  high_level:
    decomposition: high
    delegation: disabled
    execution: sequential
    agents:
      - researcher
      - analyst

  low_level:
    decomposition: low
    delegation: explicit
    execution: sequential
    agents:
      - researcher
      - analyst
    subagents:
      researcher:
        - document_search
"""


def test_load_config(tmp_path):
    config_file = tmp_path / "experiments.yaml"
    config_file.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_file)

    assert config is not None
    assert "baseline" in config.experiments
    assert "high_level" in config.experiments
    assert "low_level" in config.experiments


def test_load_config_file_not_found(tmp_path):
    config_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_config(config_file)


def test_load_invalid_yaml(tmp_path):
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text(
        "experiments: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_config(config_file)


def test_select_baseline_experiment(tmp_path):
    config_file = tmp_path / "experiments.yaml"
    config_file.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_file)
    experiment = get_experiment("baseline", config)

    assert experiment is not None


def test_select_high_level_experiment(tmp_path):
    config_file = tmp_path / "experiments.yaml"
    config_file.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_file)
    experiment = get_experiment("high_level", config)

    assert experiment is not None


def test_select_low_level_experiment(tmp_path):
    config_file = tmp_path / "experiments.yaml"
    config_file.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_file)
    experiment = get_experiment("low_level", config)

    assert experiment is not None


def test_unknown_experiment(tmp_path):
    config_file = tmp_path / "experiments.yaml"
    config_file.write_text(VALID_YAML, encoding="utf-8")

    config = load_config(config_file)

    with pytest.raises(ValueError, match="Unknown experiment"):
        get_experiment("unknown", config)