from pathlib import Path

import pytest

from shipment_tracker.storage import ShipmentManager
from shipment_tracker.models import Package
from shipment_tracker.exceptions import PackageNotFoundError, ShipmentStorageError


def test_add_and_get_package(tmp_path) -> None:
    data_file = tmp_path / "shipments.json"
    manager = ShipmentManager(data_file)

    package = Package(
        package_id="PKG-100",
        recipient="Client",
        address="789 Pine Rd",
        distance_km=300,
    )
    manager.add_package(package)

    # Reload from disk to ensure persistence works
    loaded_manager = ShipmentManager(data_file)
    loaded_package = loaded_manager.get_package("PKG-100")

    assert loaded_package.package_id == package.package_id
    assert loaded_package.recipient == package.recipient
    assert loaded_package.address == package.address


def test_get_missing_package_raises(tmp_path) -> None:
    data_file = tmp_path / "shipments.json"
    manager = ShipmentManager(data_file)

    with pytest.raises(PackageNotFoundError):
        manager.get_package("MISSING")


def test_add_duplicate_package_id_raises(tmp_path) -> None:
    data_file = tmp_path / "shipments.json"
    manager = ShipmentManager(data_file)

    package = Package(
        package_id="PKG-200",
        recipient="Client",
        address="789 Pine Rd",
        distance_km=300,
    )
    manager.add_package(package)

    duplicate = Package(
        package_id="PKG-200",
        recipient="Other",
        address="Other Address",
        distance_km=100,
    )

    with pytest.raises(ShipmentStorageError):
        manager.add_package(duplicate)


def test_list_packages_filters_by_status(tmp_path) -> None:
    data_file = tmp_path / "shipments.json"
    manager = ShipmentManager(data_file)

    pkg1 = Package(
        package_id="PKG-1",
        recipient="Alice",
        address="123 Main St",
        distance_km=50,
        status="pending",
    )
    pkg2 = Package(
        package_id="PKG-2",
        recipient="Bob",
        address="456 Oak Ave",
        distance_km=150,
        status="in_transit",
    )

    manager.add_package(pkg1)
    manager.add_package(pkg2)

    all_packages = manager.list_packages()
    pending_packages = manager.list_packages(status="pending")

    assert len(all_packages) == 2
    assert len(pending_packages) == 1
    assert pending_packages[0].package_id == "PKG-1"
