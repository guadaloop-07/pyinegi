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
from pyinegi.models import IndicatorSeries, Observation

__all__ = [
    "AuthenticationError",
    "IndicatorNotFoundError",
    "IndicatorSeries",
    "InegiClient",
    "InegiError",
    "InvalidRequestError",
    "InvalidResponseError",
    "Observation",
    "RateLimitError",
]
