from datetime import timedelta
from pathlib import Path
from typing import Final

AGENTS_CONFIGURATION_DIRECTORY: Final[Path] = Path("./agent-configs")
WEBSITE_ACCESS_TIMEOUT: Final[timedelta] = timedelta(seconds=60)
