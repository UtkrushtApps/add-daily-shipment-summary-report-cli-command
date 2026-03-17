from datetime import date, datetime
from typing import Any, Dict, Optional

from .exceptions import DataValidationError

# Allowed status and priority values
ALLOWED_STATUSES = {"pending", "in_transit", "delivered", "cancelled"}
ALLOWED_PRIORITIES = {"standard", "express"}

_DATE_FORMAT = "%Y-%m-%d"

def parse_date(date_str: str) -> date:
    """Parse a date in YYYY-MM-DD format.

    Raises DataValidationError if the format is invalid.
    """
    try:
        return datetime.strptime(date_str, _DATE_FORMAT).date()
    except ValueError as exc:
        raise DataValidationError(
            f"Invalid date format: {date_str!r}, expected YYYY-MM-DD"
        ) from exc

def format_date(value: date) -> str:
    """Format a date object as YYYY-MM-DD string."""
    return value.strftime(_DATE_FORMAT)


class Package:
    """Represents a single package shipment."""

    def __init__(
        self,
        package_id: str,
        recipient: str,
        address: str,
        distance_km: int,
        priority: str = "standard",
        status: str = "pending",
        created_at: Optional[date] = None,
        expected_delivery_date: Optional[date] = None,
    ) -> None:
        if not package_id:
            raise DataValidationError("package_id must not be empty")
        if priority not in ALLOWED_PRIORITIES:
            raise DataValidationError(f"Invalid priority: {priority!r}")
        if status not in ALLOWED_STATUSES:
            raise DataValidationError(f"Invalid status: {status!r}")
        if distance_km < 0:
            raise DataValidationError("distance_km must be non-negative")

        self.package_id = package_id
        self.recipient = recipient
        self.address = address
        self.distance_km = distance_km
        self.priority = priority
        self.status = status
        self.created_at = created_at or date.today()
        self.expected_delivery_date = expected_delivery_date

    def update_status(self, new_status: str) -> None:
        """Update the package status with validation."""
        if new_status not in ALLOWED_STATUSES:
            raise DataValidationError(f"Invalid status: {new_status!r}")
        self.status = new_status

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this package to a plain dictionary."""
        data: Dict[str, Any] = {
            "package_id": self.package_id,
            "recipient": self.recipient,
            "address": self.address,
            "distance_km": self.distance_km,
            "priority": self.priority,
            "status": self.status,
            "created_at": format_date(self.created_at),
        }

        if self.expected_delivery_date is not None:
            data["expected_delivery_date"] = format_date(self.expected_delivery_date)
        else:
            data["expected_delivery_date"] = None

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Package":
        """Create a Package instance from a dictionary.

        Raises DataValidationError if required fields are missing or invalid.
        """
        try:
            package_id = data["package_id"]
            recipient = data["recipient"]
            address = data["address"]
            distance_km = int(data["distance_km"])
            priority = data.get("priority", "standard")
            status = data.get("status", "pending")

            created_at_raw = data.get("created_at")
            if created_at_raw:
                created_at = parse_date(created_at_raw)
            else:
                created_at = date.today()

            expected_delivery_raw = data.get("expected_delivery_date")
            if expected_delivery_raw:
                expected_delivery_date = parse_date(expected_delivery_raw)
            else:
                expected_delivery_date = None
        except KeyError as exc:
            raise DataValidationError(
                f"Missing field in package data: {exc.args[0]}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise DataValidationError("Invalid type in package data") from exc

        return cls(
            package_id=package_id,
            recipient=recipient,
            address=address,
            distance_km=distance_km,
            priority=priority,
            status=status,
            created_at=created_at,
            expected_delivery_date=expected_delivery_date,
        )

    def __repr__(self) -> str:
        return (
            f"Package(package_id={self.package_id!r}, recipient={self.recipient!r}, "
            f"status={self.status!r}, priority={self.priority!r})"
        )
