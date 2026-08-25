"""Optional pandas integration for pyinegi."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from pyinegi.models import IndicatorSeries

if TYPE_CHECKING:
    import pandas as pd


def to_dataframe(series: IndicatorSeries | Iterable[IndicatorSeries]) -> pd.DataFrame:
    """Return a tidy observation-level DataFrame."""
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas support requires 'pyinegi[pandas]'.") from exc
    items = (series,) if isinstance(series, IndicatorSeries) else tuple(series)
    return pd.DataFrame.from_records(
        {
            "indicator_id": item.indicator_id,
            "period": obs.period,
            "value": obs.value,
            "geography": obs.geography,
            "frequency": item.frequency,
            "unit": item.unit,
            "unit_multiplier": item.unit_multiplier,
            "observation_status": obs.status,
            "observation_exception": obs.exception,
            "observation_source": obs.source,
            "observation_note": obs.note,
        }
        for item in items
        for obs in item.observations
    )
