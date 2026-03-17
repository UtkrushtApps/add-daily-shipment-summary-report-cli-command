from pathlib import Path
from typing import Dict, List
import json

from .models import Package
from .exceptions import ShipmentError


def _parse_packages_from_payload(payload: Dict[str, object]) -> List[Package]:
    """Convert raw JSON payload into Package objects for reporting."""
    items = payload.get("packages", [])
    packages: List[Package] = []

    for item in items:
        if not isinstance(item, dict):
            raise ShipmentError("Invalid package entry in data file")
        try:
            pkg = Package.from_dict(item)
        except Exception as exc:  # noqa: BLE001
            raise ShipmentError("Failed to parse package data for report") from exc
        packages.append(pkg)

    return packages


def _load_packages_for_report(data_file: Path) -> List[Package]:
    """Helper to load and parse packages from a data file for reporting.

    This uses the same JSON structure as the rest of the application.
    """
    # NOTE: This currently expects the file to exist and contain valid JSON.
    with data_file.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)
    return _parse_packages_from_payload(payload)


def generate_daily_summary(data_file: Path, report_file: Path) -> None:
    """Generate a daily shipment summary report.

    The report groups shipments by status and calculates a simple average
    delivery time per status in whole days, then writes a text summary to
    ``report_file``.
    """
    # Load JSON data directly from the data file. For now we keep this simple
    # and rely on the existing JSON schema used by the CLI.
    with data_file.open("r", encoding="utf-8") as fp:
        payload = json.load(fp)

    packages = _parse_packages_from_payload(payload)

    # Pre-populate the statuses we care about so they always appear
    stats: Dict[str, Dict[str, int]] = {
        "in_transit": {"count": 0, "total_days": 0},
        "delivered": {"count": 0, "total_days": 0},
        "returned": {"count": 0, "total_days": 0},
    }

    for pkg in packages:
        status = pkg.status
        if status not in stats:
            stats[status] = {"count": 0, "total_days": 0}

        group = stats[status]
        group["count"] += 1

        if pkg.expected_delivery_date:
            delta = pkg.expected_delivery_date - pkg.created_at
            # Store delivery time as whole days
            group["total_days"] += delta.days

    lines: List[str] = []
    lines.append("Daily Shipment Summary")
    lines.append("======================")
    lines.append("")

    for status in ["in_transit", "delivered", "returned"]:
        group = stats.get(status, {"count": 0, "total_days": 0})
        count = group["count"]
        total_days = group["total_days"]

        if count > 0 and total_days > 0:
            # Use integer division so the report shows whole days
            average_days = total_days // count
        else:
            average_days = 0

        lines.append(f"Status: {status}")
        lines.append(f"  Count: {count}")
        lines.append(f"  Average delivery time (days): {average_days}")
        lines.append("")

    # Also include any additional statuses that might be present in the data
    other_statuses = sorted(
        s for s in stats.keys() if s not in {"in_transit", "delivered", "returned"}
    )
    for status in other_statuses:
        group = stats[status]
        count = group["count"]
        total_days = group["total_days"]

        if count > 0 and total_days > 0:
            average_days = total_days // count
        else:
            average_days = 0

        lines.append(f"Status: {status}")
        lines.append(f"  Count: {count}")
        lines.append(f"  Average delivery time (days): {average_days}")
        lines.append("")

    try:
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:  # pragma: no cover - simple I/O wrapper
        raise ShipmentError(f"Unable to write report file: {report_file}") from exc
