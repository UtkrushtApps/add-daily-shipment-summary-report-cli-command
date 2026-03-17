from pathlib import Path
from typing import Dict, List, Optional
import json

from .models import Package
from .exceptions import ShipmentStorageError, PackageNotFoundError


class ShipmentManager:
    """Manage storage and retrieval of package shipments."""

    def __init__(self, data_file: Path) -> None:
        self._data_file = data_file
        self._shipments: Dict[str, Package] = {}
        self._load()

    @property
    def data_file(self) -> Path:
        return self._data_file

    def _load(self) -> None:
        """Load shipment data from the JSON file into memory."""
        if not self._data_file.exists():
            self._shipments = {}
            return

        try:
            raw_text = self._data_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise ShipmentStorageError(
                f"Unable to read data file: {self._data_file}"
            ) from exc

        if not raw_text.strip():
            self._shipments = {}
            return

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ShipmentStorageError(
                f"Data file contains invalid JSON: {self._data_file}"
            ) from exc

        items = payload.get("packages", [])
        shipments: Dict[str, Package] = {}
        for item in items:
            try:
                package = Package.from_dict(item)
            except Exception as exc:
                raise ShipmentStorageError(
                    "Failed to load package from data file"
                ) from exc
            shipments[package.package_id] = package

        self._shipments = shipments

    def _save(self) -> None:
        """Persist shipment data to the JSON file."""
        data = {
            "packages": [pkg.to_dict() for pkg in self._shipments.values()]
        }

        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            self._data_file.write_text(
                json.dumps(data, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            raise ShipmentStorageError(
                f"Unable to write data file: {self._data_file}"
            ) from exc

    def add_package(self, package: Package) -> None:
        """Add a new package to storage.

        Raises ShipmentStorageError if a package with the same ID already exists.
        """
        if package.package_id in self._shipments:
            raise ShipmentStorageError(
                f"A package with this ID already exists: {package.package_id}"
            )

        self._shipments[package.package_id] = package
        self._save()

    def get_package(self, package_id: str) -> Package:
        """Return a package by its ID.

        Raises PackageNotFoundError if the package does not exist.
        """
        try:
            return self._shipments[package_id]
        except KeyError as exc:
            raise PackageNotFoundError(f"Package not found: {package_id}") from exc

    def update_status(self, package_id: str, new_status: str) -> Package:
        """Update the status of a package and persist the change."""
        package = self.get_package(package_id)
        package.update_status(new_status)
        self._save()
        return package

    def list_packages(self, status: Optional[str] = None) -> List[Package]:
        """Return all packages, optionally filtered by status."""
        if status is None:
            return list(self._shipments.values())
        return [pkg for pkg in self._shipments.values() if pkg.status == status]

    def initialize_storage(self) -> None:
        """Create the data file on disk if it does not exist.

        Existing data is left as-is.
        """
        if not self._data_file.exists():
            self._save()
