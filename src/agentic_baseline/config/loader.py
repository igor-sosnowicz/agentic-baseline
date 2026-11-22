
from pathlib import Path
from functools import lru_cache

import yaml

from agentic_baseline.config.schemas import ExperimentsConfig


CONFIG_DIRECTORY = Path(__file__).resolve().parent
CONFIG_FILE = CONFIG_DIRECTORY / "experiments.yaml"


def load_config(config_path: Path | str = CONFIG_FILE) -> ExperimentsConfig:
    """
    Load and validate the experiments configuration.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Validated experiments configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If the YAML file is empty or invalid.
    """
    path = Path(config_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            raw_config = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Invalid YAML configuration: {exc}"
        ) from exc

    if not isinstance(raw_config, dict):
        raise ValueError(
            "Configuration must contain a YAML mapping."
        )

    return ExperimentsConfig.model_validate(raw_config)


def get_experiment(
    experiment_name: str,
    config: ExperimentsConfig | None = None,
) -> dict:
    """
    Retrieve a specific experiment configuration.

    Args:
        experiment_name: Name of the experiment variant.
        config: Previously loaded configuration.
               If omitted, the default configuration is loaded.

    Returns:
        Configuration of the selected experiment.

    Raises:
        ValueError: If the experiment does not exist.
    """
    if config is None:
        config = load_config()

    experiments = config.experiments

    if experiment_name not in experiments:
        available = ", ".join(experiments.keys())
        raise ValueError(
            f"Unknown experiment '{experiment_name}'. "
            f"Available experiments: {available}"
        )

    return experiments[experiment_name]