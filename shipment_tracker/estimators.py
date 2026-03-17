from datetime import date, timedelta

from .models import ALLOWED_PRIORITIES
from .exceptions import DataValidationError


def calculate_transit_days(distance_km: int, priority: str) -> int:
    """Estimate number of transit days based on distance and priority.

    This is a simple heuristic suitable for small-scale planning.
    """
    if distance_km < 0:
        raise DataValidationError("distance_km must be non-negative")
    if priority not in ALLOWED_PRIORITIES:
        raise DataValidationError(f"Invalid priority: {priority!r}")

    # Basic distance-based calculation
    if distance_km == 0:
        base_days = 1
    elif distance_km <= 200:
        base_days = 2
    elif distance_km <= 800:
        base_days = 3
    else:
        extra_segments = (distance_km - 800 + 399) // 400  # ceil division
        base_days = 3 + extra_segments

    # Express priority reduces time but never below 1 day
    if priority == "express":
        return max(1, base_days - 1)

    return base_days


def estimate_delivery_date(shipping_date: date, distance_km: int, priority: str) -> date:
    """Estimate a delivery date given a shipping date, distance, and priority."""
    transit_days = calculate_transit_days(distance_km, priority)
    return shipping_date + timedelta(days=transit_days)
