from datetime import date

import pytest

from shipment_tracker.estimators import calculate_transit_days, estimate_delivery_date
from shipment_tracker.exceptions import DataValidationError


def test_calculate_transit_days_standard() -> None:
    days = calculate_transit_days(100, "standard")
    assert days >= 1


def test_calculate_transit_days_express_is_not_longer() -> None:
    standard = calculate_transit_days(600, "standard")
    express = calculate_transit_days(600, "express")
    assert express <= standard


def test_calculate_transit_days_negative_distance_raises() -> None:
    with pytest.raises(DataValidationError):
        calculate_transit_days(-5, "standard")


def test_estimate_delivery_date_adds_days() -> None:
    shipping_date = date(2023, 1, 1)
    estimated = estimate_delivery_date(shipping_date, 100, "standard")
    assert estimated > shipping_date
