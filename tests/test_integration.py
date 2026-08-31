"""Opt-in integration coverage for the live INEGI API."""

from __future__ import annotations

import os

import pytest

from pyinegi import IndicatorSeries, InegiClient, Observation

pytestmark = pytest.mark.integration


def test_public_indicator_returns_typed_observations() -> None:
    """The stable public indicator in the quick-start guide returns typed data."""
    token = os.getenv("INEGI_TOKEN")
    if not token:
        pytest.skip("INEGI_TOKEN is required for live INEGI API tests.")

    series = InegiClient(token=token).get_indicator("1002000001", geography="00")

    assert isinstance(series, tuple)
    assert series
    assert all(isinstance(item, IndicatorSeries) for item in series)
    assert all(item.observations for item in series)
    assert all(
        isinstance(observation, Observation) for item in series for observation in item.observations
    )
