from decimal import Decimal

from pyinegi.models import IndicatorSeries, Observation
from pyinegi.pandas import to_dataframe


def test_to_dataframe_returns_tidy_observations():
    series = IndicatorSeries(
        indicator_id="1002000001",
        frequency="A",
        topic=None,
        unit="Persons",
        unit_multiplier="0",
        note=None,
        source=None,
        last_updated=None,
        status=None,
        observations=(Observation(period="2024", value=Decimal("10"), geography="00"),),
    )

    frame = to_dataframe(series)

    assert frame.to_dict("records")[0]["value"] == Decimal("10")
    assert frame.to_dict("records")[0]["indicator_id"] == "1002000001"
