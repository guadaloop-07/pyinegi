from decimal import Decimal

import pytest
import requests

from pyinegi import (
    AuthenticationError,
    CatalogEntry,
    InegiClient,
    InvalidRequestError,
    InvalidResponseError,
    RateLimitError,
)


class Response:
    def __init__(self, status, payload):
        self.status_code, self.payload = status, payload

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError()


class Session:
    def __init__(self, responses):
        self.responses, self.headers, self.calls = responses, {}, []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def payload(value="10"):
    return {
        "Series": [
            {
                "INDICADOR": "1002000001",
                "FREQ": "A",
                "OBSERVATIONS": [{"TIME_PERIOD": "2024", "OBS_VALUE": value, "COBER_GEO": "00"}],
            }
        ]
    }


def test_get_indicator_builds_url_and_parses_response():
    session = Session([Response(200, payload())])
    result = InegiClient("secret", session=session).get_indicator("1002000001")
    assert "/INDICATOR/1002000001/es/00/false/BISE/2.0/secret" in session.calls[0][0]
    assert session.calls[0][1]["params"] == {"type": "json"}
    assert result[0].observations[0].value == Decimal("10")


def test_get_catalog_builds_url_and_parses_records():
    session = Session(
        [Response(200, {"CODE": [{"Value": "1002000001", "Description": "Población total"}]})]
    )
    result = InegiClient("secret", session=session).get_catalog("CL_INDICATOR", "1002000001")
    assert "/CL_INDICATOR/1002000001/es/BISE/2.0/secret" in session.calls[0][0]
    assert result == (CatalogEntry("1002000001", "Población total"),)


def test_get_catalog_supports_all_records_and_validates_arguments():
    session = Session([Response(200, {"CODE": [{"value": 96, "description": "Personas"}]})])
    result = InegiClient("token", session=session).get_catalog("CL_UNIT", language="en")
    assert "/CL_UNIT/null/en/BISE/2.0/token" in session.calls[0][0]
    assert result[0].value == "96"
    client = InegiClient("token")
    with pytest.raises(InvalidRequestError):
        client.get_catalog("CL_UNKNOWN")
    with pytest.raises(InvalidRequestError):
        client.get_catalog("CL_UNIT", "96/invalid")
    with pytest.raises(InvalidRequestError):
        client.get_catalog("CL_UNIT", language="fr")


def test_get_catalog_rejects_invalid_records():
    client = InegiClient(
        "token",
        session=Session(
            [Response(200, {"CODE": [{"Value": "96"}]}), Response(200, {"CODE": "bad"})]
        ),
    )
    with pytest.raises(InvalidResponseError):
        client.get_catalog("CL_UNIT", "96")
    with pytest.raises(InvalidResponseError):
        client.get_catalog("CL_UNIT", "96")


def test_latest_and_environment_token(monkeypatch):
    monkeypatch.setenv("INEGI_TOKEN", " token ")
    session = Session([Response(200, payload())])
    InegiClient(session=session).get_latest_indicator("1002000001", language="en")
    assert "/en/00/true/" in session.calls[0][0]


def test_rejects_missing_token_and_invalid_arguments():
    with pytest.raises(AuthenticationError):
        InegiClient("")
    client = InegiClient("token")
    with pytest.raises(InvalidRequestError):
        client.get_indicator("x/y")
    with pytest.raises(InvalidRequestError):
        client.get_indicator("1", language="fr")


def test_retries_and_maps_rate_limit():
    delays = []
    session = Session([Response(503, {}), Response(200, payload())])
    assert InegiClient(
        "token", session=session, max_retries=1, retry_backoff=0.5, sleep=delays.append
    ).get_indicator("1")
    assert delays == [0.5]
    with pytest.raises(RateLimitError):
        InegiClient("token", session=Session([Response(429, {})])).get_indicator("1")


def test_rejects_bad_json_and_values():
    with pytest.raises(InvalidResponseError):
        InegiClient("token", session=Session([Response(200, ValueError())])).get_indicator("1")
    with pytest.raises(InvalidResponseError):
        InegiClient("token", session=Session([Response(200, payload("bad"))])).get_indicator("1")


def test_validates_constructor_arguments():
    with pytest.raises(InvalidRequestError):
        InegiClient("token", timeout=0)
    with pytest.raises(InvalidRequestError):
        InegiClient("token", max_retries=-1)
    with pytest.raises(InvalidRequestError):
        InegiClient("token", retry_backoff=-1)


def test_preserves_api_error_messages_and_maps_not_found():
    client = InegiClient(
        "token", session=Session([Response(404, {"Message": "Missing indicator"})])
    )

    with pytest.raises(Exception, match="Missing indicator"):
        client.get_indicator("1")


def test_raises_generic_error_for_unrecoverable_network_failure():
    class FailingSession:
        headers = {}

        def get(self, *args, **kwargs):
            raise requests.ConnectionError("offline")

    with pytest.raises(Exception, match="request failed"):
        InegiClient("token", session=FailingSession()).get_indicator("1")


def test_maps_unexpected_http_errors_and_rejects_non_object_json():
    with pytest.raises(Exception, match="HTTP error"):
        InegiClient("token", session=Session([Response(400, {})])).get_indicator("1")
    with pytest.raises(InvalidResponseError):
        InegiClient("token", session=Session([Response(200, [])])).get_indicator("1")


def test_parser_rejects_missing_series_fields_and_invalid_observations():
    invalid = {"Series": [{"INDICADOR": "1", "OBSERVATIONS": [{"OBS_VALUE": "10"}]}]}
    with pytest.raises(InvalidResponseError):
        InegiClient("token", session=Session([Response(200, invalid)])).get_indicator("1")
    with pytest.raises(InvalidResponseError):
        InegiClient("token", session=Session([Response(200, {"Series": "bad"})])).get_indicator("1")
