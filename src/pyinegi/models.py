"""Typed data models returned by the INEGI Indicators API."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Observation:
    """One observation published for an indicator and geographic area."""

    period: str
    value: Decimal | None
    exception: str | None = None
    status: str | None = None
    source: str | None = None
    note: str | None = None
    geography: str | None = None


@dataclass(frozen=True, slots=True)
class IndicatorSeries:
    """Indicator metadata and its observations for a geographic area."""

    indicator_id: str
    frequency: str | None
    topic: str | None
    unit: str | None
    unit_multiplier: str | None
    note: str | None
    source: str | None
    last_updated: str | None
    status: str | None
    observations: tuple[Observation, ...]
