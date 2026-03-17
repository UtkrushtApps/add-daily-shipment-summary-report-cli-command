# Shipment Tracker CLI

A small Python command-line tool for a logistics company to track package shipments.

## Features

- Track packages with ID, recipient, address, distance, priority, and status
- Load and save shipment data from a JSON file
- Estimate delivery dates based on distance and priority
- Simple, script-friendly CLI built with Python's standard library
- JSON storage path configurable via an environment variable

## Project structure

- `shipment_tracker/`
  - `__init__.py` – package exports
  - `__main__.py` – allows `python -m shipment_tracker`
  - `cli.py` – command-line interface and argument parsing
  - `config.py` – configuration helpers (data file location)
  - `exceptions.py` – custom exception types
  - `models.py` – `Package` class and basic validation helpers
  - `storage.py` – `ShipmentManager` for loading/saving shipments
  - `estimators.py` – helper functions for delivery estimates
- `tests/` – pytest-based unit tests for core functionality

## Installation

This project uses only the Python standard library at runtime. Pytest is used for tests.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

You can run the CLI either via the module entry point:

```bash
python -m shipment_tracker --help
```

or by calling the CLI module directly:

```bash
python -m shipment_tracker.cli --help
```

### Data file location

By default, shipment data is stored in:

- `./data/shipments.json` (relative to the current working directory)

You can override this path using the `--data-file` option:

```bash
python -m shipment_tracker list --data-file ./my_shipments.json
```

or via the `SHIPMENT_TRACKER_DATA_PATH` environment variable:

```bash
export SHIPMENT_TRACKER_DATA_PATH=/tmp/shipments.json
python -m shipment_tracker list
```

### Initialize the data file

```bash
python -m shipment_tracker init-db
```

This creates the JSON data file (and parent directory) if it does not already exist.

### Add a package

```bash
python -m shipment_tracker add PKG-001 "Alice Smith" "123 Main St, Springfield" 250 --priority express
```

This command:

- Adds a new package with ID `PKG-001`
- Uses the specified recipient, address, distance, and priority
- Automatically computes and stores an estimated delivery date

### List packages

```bash
python -m shipment_tracker list
python -m shipment_tracker list --status delivered
```

### Show a single package

```bash
python -m shipment_tracker show PKG-001
```

### Update package status

```bash
python -m shipment_tracker update-status PKG-001 in_transit
python -m shipment_tracker update-status PKG-001 delivered
```

### Estimate delivery date without storing a package

```bash
python -m shipment_tracker estimate 600 --priority express --shipping-date 2023-01-15
```

## JSON data format

The shipment data file is a UTF-8 encoded JSON document with the following structure:

```json
{
  "packages": [
    {
      "package_id": "PKG-001",
      "recipient": "Alice Smith",
      "address": "123 Main St, Springfield",
      "distance_km": 250,
      "priority": "express",
      "status": "in_transit",
      "created_at": "2023-01-10",
      "expected_delivery_date": "2023-01-12"
    }
  ]
}
```

## Running tests

```bash
pytest
```

The tests cover the `Package` model, the `ShipmentManager` storage layer, and the delivery estimator helpers.
