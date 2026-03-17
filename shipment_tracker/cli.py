import argparse
from pathlib import Path
from datetime import date
import sys

from .config import get_default_data_path
from .storage import ShipmentManager
from .models import (
    Package,
    ALLOWED_STATUSES,
    ALLOWED_PRIORITIES,
    parse_date,
)
from .estimators import estimate_delivery_date
from .exceptions import ShipmentError, PackageNotFoundError


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="shipment-tracker",
        description="Track package shipments for a small logistics company.",
    )

    parser.add_argument(
        "--data-file",
        type=Path,
        default=get_default_data_path(),
        help="Path to the JSON data file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init-db
    p_init = subparsers.add_parser("init-db", help="Initialize the shipment data file")
    p_init.set_defaults(func=handle_init)

    # add
    p_add = subparsers.add_parser("add", help="Add a new package")
    p_add.add_argument("package_id", help="Unique ID for the package")
    p_add.add_argument("recipient", help="Recipient name")
    p_add.add_argument("address", help="Delivery address")
    p_add.add_argument("distance_km", type=int, help="Distance to destination in kilometers")
    p_add.add_argument(
        "--priority",
        choices=sorted(ALLOWED_PRIORITIES),
        default="standard",
        help="Shipping priority (default: standard)",
    )
    p_add.set_defaults(func=handle_add)

    # list
    p_list = subparsers.add_parser("list", help="List packages")
    p_list.add_argument(
        "--status",
        choices=sorted(ALLOWED_STATUSES),
        help="Filter packages by status",
    )
    p_list.set_defaults(func=handle_list)

    # show
    p_show = subparsers.add_parser("show", help="Show details for a package")
    p_show.add_argument("package_id", help="Package ID")
    p_show.set_defaults(func=handle_show)

    # update-status
    p_update = subparsers.add_parser("update-status", help="Update status of a package")
    p_update.add_argument("package_id", help="Package ID")
    p_update.add_argument(
        "status",
        choices=sorted(ALLOWED_STATUSES),
        help="New status",
    )
    p_update.set_defaults(func=handle_update_status)

    # estimate
    p_estimate = subparsers.add_parser(
        "estimate", help="Estimate delivery date for a potential shipment"
    )
    p_estimate.add_argument("distance_km", type=int, help="Distance in kilometers")
    p_estimate.add_argument(
        "--priority",
        choices=sorted(ALLOWED_PRIORITIES),
        default="standard",
        help="Shipping priority (default: standard)",
    )
    p_estimate.add_argument(
        "--shipping-date",
        help="Planned shipping date (YYYY-MM-DD). Defaults to today.",
    )
    p_estimate.set_defaults(func=handle_estimate)

    return parser


def create_manager_from_args(args: argparse.Namespace) -> ShipmentManager:
    """Create a ShipmentManager using CLI arguments."""
    return ShipmentManager(args.data_file)


def handle_init(args: argparse.Namespace) -> None:
    manager = create_manager_from_args(args)
    manager.initialize_storage()
    print(f"Initialized shipment data file at {manager.data_file}")


def handle_add(args: argparse.Namespace) -> None:
    manager = create_manager_from_args(args)

    pkg = Package(
        package_id=args.package_id,
        recipient=args.recipient,
        address=args.address,
        distance_km=args.distance_km,
        priority=args.priority,
    )

    # Compute and store an estimated delivery date
    estimated = estimate_delivery_date(
        pkg.created_at,
        pkg.distance_km,
        pkg.priority,
    )
    pkg.expected_delivery_date = estimated

    manager.add_package(pkg)

    print(f"Added package {pkg.package_id} for {pkg.recipient}")
    print(f"Estimated delivery date: {estimated.isoformat()}")


def handle_list(args: argparse.Namespace) -> None:
    manager = create_manager_from_args(args)
    packages = manager.list_packages(status=args.status)

    if not packages:
        print("No packages found.")
        return

    header = f"{'ID':<12} {'Recipient':<20} {'Status':<12} {'Priority':<10} {'ETA':<10}"
    print(header)
    print("-" * len(header))

    for pkg in packages:
        eta = pkg.expected_delivery_date.isoformat() if pkg.expected_delivery_date else "-"
        print(
            f"{pkg.package_id:<12} {pkg.recipient:<20} {pkg.status:<12} "
            f"{pkg.priority:<10} {eta:<10}"
        )


def handle_show(args: argparse.Namespace) -> None:
    manager = create_manager_from_args(args)
    pkg = manager.get_package(args.package_id)

    print(f"ID: {pkg.package_id}")
    print(f"Recipient: {pkg.recipient}")
    print(f"Address: {pkg.address}")
    print(f"Distance (km): {pkg.distance_km}")
    print(f"Priority: {pkg.priority}")
    print(f"Status: {pkg.status}")
    print(f"Created at: {pkg.created_at.isoformat()}")
    if pkg.expected_delivery_date:
        print(f"Expected delivery date: {pkg.expected_delivery_date.isoformat()}")


def handle_update_status(args: argparse.Namespace) -> None:
    manager = create_manager_from_args(args)
    pkg = manager.update_status(args.package_id, args.status)
    print(f"Updated package {pkg.package_id} to status {pkg.status}")


def handle_estimate(args: argparse.Namespace) -> None:
    if args.shipping_date:
        ship_date = parse_date(args.shipping_date)
    else:
        ship_date = date.today()

    estimated = estimate_delivery_date(ship_date, args.distance_km, args.priority)
    print(f"Estimated delivery date: {estimated.isoformat()}")


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        args.func(args)
    except PackageNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ShipmentError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Aborted by user.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
