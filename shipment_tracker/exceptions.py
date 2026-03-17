class ShipmentError(Exception):
    """Base exception for shipment tracker errors."""


class ShipmentStorageError(ShipmentError):
    """Raised when loading or saving shipments fails."""


class PackageNotFoundError(ShipmentError):
    """Raised when a package ID cannot be found."""


class DataValidationError(ShipmentError):
    """Raised when input or stored data is invalid."""
