"""A typed Python client for the INEGI Indicators API."""

from pyinegi.client import InegiClient
from pyinegi.exceptions import (
    AuthenticationError,
    IndicatorNotFoundError,
    InegiError,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
)
from pyinegi.models import CatalogEntry, IndicatorSeries, Observation

__all__ = [
    "AuthenticationError",
    "CatalogEntry",
    "IndicatorNotFoundError",
    "IndicatorSeries",
    "InegiClient",
    "InegiError",
    "InvalidRequestError",
    "InvalidResponseError",
    "Observation",
    "RateLimitError",
]
