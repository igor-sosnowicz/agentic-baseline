
from pathlib import Path
from datetime import timedelta
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DOCUMENTS_DIRECTORY = PROJECT_ROOT / "data" / "documents"

AGENTS_CONFIGURATION_DIRECTORY: Final[Path] = (
    PROJECT_ROOT / "agent-configs"
)

WEBSITE_ACCESS_TIMEOUT: Final[timedelta] = timedelta(seconds=60)