from datetime import date

import pytest

from shipment_tracker.models import (
    Package,
    ALLOWED_STATUSES,
    ALLOWED_PRIORITIES,
)
from shipment_tracker.exceptions import DataValidationError


def test_package_to_from_dict_roundtrip() -> None:
    pkg = Package(
        package_id="PKG-1",
        recipient="Alice",
        address="123 Main St",
        distance_km=100,
        priority="express",
        status="pending",
        created_at=date(2023, 1, 10),
    )

    pkg_dict = pkg.to_dict()
    restored = Package.from_dict(pkg_dict)

    assert restored.package_id == pkg.package_id
    assert restored.recipient == pkg.recipient
    assert restored.address == pkg.address
    assert restored.distance_km == pkg.distance_km
    assert restored.priority == pkg.priority
    assert restored.status == pkg.status
    assert restored.created_at == pkg.created_at


def test_invalid_status_raises() -> None:
    with pytest.raises(DataValidationError):
        Package(
            package_id="PKG-2",
            recipient="Bob",
            address="456 Oak Ave",
            distance_km=50,
            priority="standard",
            status="unknown",
        )


def test_invalid_priority_raises() -> None:
    with pytest.raises(DataValidationError):
        Package(
            package_id="PKG-3",
            recipient="Bob",
            address="456 Oak Ave",
            distance_km=50,
            priority="overnight",
        )


def test_allowed_status_constants() -> None:
    assert "pending" in ALLOWED_STATUSES
    assert "in_transit" in ALLOWED_STATUSES
    assert "delivered" in ALLOWED_STATUSES
    assert "cancelled" in ALLOWED_STATUSES


def test_allowed_priority_constants() -> None:
    assert "standard" in ALLOWED_PRIORITIES
    assert "express" in ALLOWED_PRIORITIES
