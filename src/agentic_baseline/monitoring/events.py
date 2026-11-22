
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4


class EventLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def log(self, event_type: str, **data) -> None:
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            **data,
        }

        with self._lock:
            with self.path.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(
                    json.dumps(
                        event,
                        ensure_ascii=False,
                        default=str,
                    ) + "\n"
                )