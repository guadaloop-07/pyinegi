"""HTTP client for the INEGI Indicators API."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

import requests

from pyinegi.exceptions import (
    AuthenticationError,
    IndicatorNotFoundError,
    InegiError,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
)
from pyinegi.models import CatalogEntry, IndicatorSeries
from pyinegi.parsing import parse_catalog_response, parse_indicator_response

DEFAULT_BASE_URL = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml"
_SUPPORTED_CATALOGS = frozenset(
    {"CL_FREQ", "CL_GEO_AREA", "CL_INDICATOR", "CL_NOTE", "CL_SOURCE", "CL_TOPIC", "CL_UNIT"}
)


class InegiClient:
    """Client for JSON indicators from INEGI's Banco de Indicadores API."""

    def __init__(
        self,
        token: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 0,
        retry_backoff: float = 1.0,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        supplied = os.getenv("INEGI_TOKEN") if token is None else token
        self.token = _required(supplied, "INEGI API token", AuthenticationError)
        if timeout <= 0:
            raise InvalidRequestError("timeout must be greater than zero.")
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise InvalidRequestError("max_retries must be a non-negative integer.")
        if (
            isinstance(retry_backoff, bool)
            or not isinstance(retry_backoff, int | float)
            or retry_backoff < 0
        ):
            raise InvalidRequestError("retry_backoff must be a non-negative number.")
        self.base_url, self.timeout, self.max_retries, self.retry_backoff = (
            base_url.rstrip("/"),
            timeout,
            max_retries,
            float(retry_backoff),
        )
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._sleep = sleep

    def get_indicator(
        self,
        indicator_id: str,
        *,
        geography: str = "00",
        language: str = "es",
        latest: bool = False,
        source: str = "BISE",
    ) -> tuple[IndicatorSeries, ...]:
        """Return historical data by default, or only the latest value when requested."""
        if language not in {"es", "en"}:
            raise InvalidRequestError("language must be either 'es' or 'en'.")
        if not isinstance(latest, bool):
            raise InvalidRequestError("latest must be a boolean.")
        identifier, geo, data_source = (
            _segment(indicator_id, "indicator_id"),
            _segment(geography, "geography"),
            _segment(source, "source"),
        )
        path = (
            f"/INDICATOR/{identifier}/{language}/{geo}/{str(latest).lower()}"
            f"/{data_source}/2.0/{self.token}"
        )
        return parse_indicator_response(self._get_json(path))

    def get_catalog(
        self,
        catalog: str,
        record_id: str | None = None,
        *,
        language: str = "es",
        source: str = "BISE",
    ) -> tuple[CatalogEntry, ...]:
        """Return one or all records from a documented INEGI metadata catalog."""
        if language not in {"es", "en"}:
            raise InvalidRequestError("language must be either 'es' or 'en'.")
        catalog_name = _segment(catalog, "catalog").upper()
        if catalog_name not in _SUPPORTED_CATALOGS:
            supported = ", ".join(sorted(_SUPPORTED_CATALOGS))
            raise InvalidRequestError(f"catalog must be one of: {supported}.")
        identifier = "null" if record_id is None else _segment(record_id, "record_id")
        data_source = _segment(source, "source")
        path = f"/{catalog_name}/{identifier}/{language}/{data_source}/2.0/{self.token}"
        return parse_catalog_response(self._get_json(path))

    def get_latest_indicator(
        self,
        indicator_id: str,
        *,
        geography: str = "00",
        language: str = "es",
        source: str = "BISE",
    ) -> tuple[IndicatorSeries, ...]:
        """Return only the latest observation for an INEGI indicator."""
        return self.get_indicator(
            indicator_id, geography=geography, language=language, latest=True, source=source
        )

    def _get_json(self, path: str) -> dict[str, Any]:
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(
                    f"{self.base_url}{path}", params={"type": "json"}, timeout=self.timeout
                )
            except requests.RequestException as exc:
                if attempt < self.max_retries:
                    self._retry(attempt)
                    continue
                raise InegiError("The INEGI API request failed.") from exc
            payload = _json(response)
            message = _message(payload)
            if response.status_code in {401, 403}:
                raise AuthenticationError(message or "The INEGI API rejected the token.")
            if response.status_code == 404:
                raise IndicatorNotFoundError(
                    message or "The requested INEGI indicator was not found."
                )
            if response.status_code == 429:
                if attempt < self.max_retries:
                    self._retry(attempt)
                    continue
                raise RateLimitError(message or "The INEGI API rate limit has been exceeded.")
            if 500 <= response.status_code < 600 and attempt < self.max_retries:
                self._retry(attempt)
                continue
            try:
                response.raise_for_status()
            except requests.RequestException as exc:
                raise InegiError(message or "The INEGI API returned an HTTP error.") from exc
            return payload
        raise AssertionError("Retry loop must return or raise.")

    def _retry(self, attempt: int) -> None:
        delay = self.retry_backoff * 2**attempt
        if delay:
            self._sleep(delay)


def _required(value: object, name: str, error: type[InegiError]) -> str:
    if not isinstance(value, str) or not value.strip():
        raise error(f"A non-empty {name} is required.")
    return value.strip()


def _segment(value: object, name: str) -> str:
    text = _required(value, name, InvalidRequestError)
    if any(character in text for character in "/?#"):
        raise InvalidRequestError(f"{name} must be a single URL path segment.")
    return text


def _json(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise InvalidResponseError("The INEGI API returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise InvalidResponseError("The INEGI API returned a JSON value other than an object.")
    return payload


def _message(payload: dict[str, Any]) -> str | None:
    return next(
        (
            value.strip()
            for key in ("message", "Message", "error", "Error")
            if isinstance(value := payload.get(key), str) and value.strip()
        ),
        None,
    )
