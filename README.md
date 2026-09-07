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

### Jupyter notebooks

If you use Jupyter and prefer not to configure an environment variable in a
terminal, prompt for the token when the notebook starts. Run this cell, then
paste the token into the input field that appears and press Enter:

```python
from getpass import getpass
from pyinegi import InegiClient

token = getpass("Paste your INEGI API token: ")
client = InegiClient(token=token)
```

`"Paste your INEGI API token: "` is only the text shown next to the input
field; do not replace it with the token. `getpass` hides what you type, so the
token is not displayed in the notebook output or written directly in the cell.
You can then use `client` as usual:

```python
series = client.get_latest_indicator("1002000001")
for observation in series[0].observations:
    print(observation.period, observation.value)
```

## Metadata catalogs

Retrieve indicator metadata or another documented catalog with `get_catalog`:

```python
entries = InegiClient().get_catalog("CL_INDICATOR", "1002000001")
print(entries[0].description)
```

Pass `record_id=None` to retrieve every record in a supported catalog.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). The project uses protected-main pull requests, English Conventional Commits, pre-commit hooks, and GitHub Actions quality gates.

## License

[MIT](LICENSE)
