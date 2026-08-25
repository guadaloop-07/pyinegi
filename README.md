# pyinegi

A typed Python client for querying indicators and metadata from the [INEGI Indicators API](https://www.inegi.org.mx/servicios/api_indicadores.html).

## Installation

```console
pip install pyinegi
```

## Quick start

Set your API token outside source code, then query an indicator:

```console
export INEGI_TOKEN="your-token"
```

```python
from pyinegi import InegiClient

series = InegiClient().get_indicator("1002000001", geography="00")
for observation in series[0].observations:
    print(observation.period, observation.value)
```

Install `pyinegi[pandas]` to use `pyinegi.pandas.to_dataframe`.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). The project uses protected-main pull requests, English Conventional Commits, pre-commit hooks, and GitHub Actions quality gates.

## License

[MIT](LICENSE)
