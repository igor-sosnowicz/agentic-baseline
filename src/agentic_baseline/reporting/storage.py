
import json
from pathlib import Path
from uuid import uuid4

from agentic_baseline.reporting.schemas import Report


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIRECTORY = PROJECT_ROOT / "data" / "reports"


def save_report(report: Report) -> dict[str, str]:
    """
    Save a validated report as a JSON file.

    Returns:
        Confirmation containing report_id and file path.
    """
    REPORTS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    report_id = str(uuid4())
    file_path = REPORTS_DIRECTORY / f"{report_id}.json"

    report_data = report.model_dump(mode="json")

    with file_path.open("x", encoding="utf-8") as file:
        json.dump(
            report_data,
            file,
            ensure_ascii=False,
            indent=4,
        )

    if not file_path.is_file():
        raise OSError("Report could not be saved.")

    return {
        "status": "saved",
        "report_id": report_id,
        "file_path": str(file_path),
    }