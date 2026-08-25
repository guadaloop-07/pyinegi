"""Public exceptions raised by pyinegi."""


class InegiError(Exception):
    """Base exception for errors raised by the INEGI client."""


class AuthenticationError(InegiError):
    """Raised when an INEGI API token is absent or rejected."""


class InvalidRequestError(InegiError):
    """Raised when client input is invalid before a request is sent."""


class IndicatorNotFoundError(InegiError):
    """Raised when INEGI does not find an indicator or geography."""


class RateLimitError(InegiError):
    """Raised when INEGI rate limits a request."""


class InvalidResponseError(InegiError):
    """Raised when INEGI returns an invalid response."""
