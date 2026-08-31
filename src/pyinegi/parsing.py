"""Parsing helpers for JSON responses from the INEGI Indicators API."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from pyinegi.exceptions import InvalidResponseError
from pyinegi.models import CatalogEntry, IndicatorSeries, Observation


def parse_catalog_response(payload: dict[str, Any]) -> tuple[CatalogEntry, ...]:
    """Parse a JSON metadata catalog response into immutable typed models."""
    raw = payload.get("CODE")
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise InvalidResponseError("The INEGI response does not contain a valid 'CODE' list.")
    result = []
    for item in raw:
        if not isinstance(item, dict):
            raise InvalidResponseError("The INEGI response contains an invalid catalog record.")
        value = _text(item.get("Value", item.get("value")))
        description = _text(item.get("Description", item.get("description")))
        if value is None or description is None:
            raise InvalidResponseError("The INEGI response contains an incomplete catalog record.")
        result.append(CatalogEntry(value, description))
    return tuple(result)


def parse_indicator_response(payload: dict[str, Any]) -> tuple[IndicatorSeries, ...]:
    """Parse a JSON indicator response into immutable typed models."""
    raw = payload.get("Series")
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raise InvalidResponseError("The INEGI response does not contain a valid 'Series' list.")
    result = []
    for item in raw:
        if not isinstance(item, dict) or (identifier := _text(item.get("INDICADOR"))) is None:
            raise InvalidResponseError("The INEGI response contains an invalid series record.")
        observations = item.get("OBSERVATIONS", [])
        if not isinstance(observations, list):
            raise InvalidResponseError("The INEGI response contains invalid observations.")
        parsed = []
        for record in observations:
            if not isinstance(record, dict) or (period := _text(record.get("TIME_PERIOD"))) is None:
                raise InvalidResponseError(
                    "The INEGI response contains an invalid observation record."
                )
            parsed.append(
                Observation(
                    period,
                    _decimal(record.get("OBS_VALUE")),
                    _text(record.get("OBS_EXCEPTION")),
                    _text(record.get("OBS_STATUS")),
                    _text(record.get("OBS_SOURCE")),
                    _text(record.get("OBS_NOTE")),
                    _text(record.get("COBER_GEO")),
                )
            )
        result.append(
            IndicatorSeries(
                identifier,
                _text(item.get("FREQ")),
                _text(item.get("TOPIC")),
                _text(item.get("UNIT")),
                _text(item.get("UNIT_MULT")),
                _text(item.get("NOTE")),
                _text(item.get("SOURCE")),
                _text(item.get("LASTUPDATE")),
                _text(item.get("STATUS")),
                tuple(parsed),
            )
        )
    return tuple(result)


def _text(value: Any) -> str | None:
    return (
        value if isinstance(value, str) else str(value) if isinstance(value, int | float) else None
    )


def _decimal(value: Any) -> Decimal | None:
    text = _text(value)
    if text is None or text in {"", "N/A", "NA"}:
        return None
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise InvalidResponseError(
            "The INEGI response contains a non-numeric observation value."
        ) from exc
