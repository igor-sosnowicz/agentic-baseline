
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from agentic_baseline.constants import PROJECT_ROOT


@dataclass
class RunContext:
    experiment_id: str
    run_id: str
    instance_id: str
    trace_id: str
    started_at: datetime
    output_dir: Path

    @classmethod
    def create(
        cls,
        experiment_id: str,
        instance_id: str,
    ) -> "RunContext":
        run_id = str(uuid4())

        output_dir = (
            PROJECT_ROOT / "data" / "experiments"
            / experiment_id
            / f"run_{run_id}"
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        return cls(
            experiment_id=experiment_id,
            run_id=run_id,
            instance_id=instance_id,
            trace_id=str(uuid4()),
            started_at=datetime.now(timezone.utc),
            output_dir=output_dir.resolve(),
        )