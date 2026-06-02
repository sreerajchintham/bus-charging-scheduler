# bus-charging-scheduler

Bus charging scheduler (Python, OR-Tools CP-SAT, Streamlit).

## Development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install
make test
```

Runtime-only install:

```bash
pip install -r requirements.txt
pip install -e .
```

Dependencies are listed in `requirements.txt` / `requirements-dev.txt` at the repo root (source of truth for `pip install`; `pyproject.toml` stays in sync for packaging).

### Running tests (read this if `pytest` crashes)

**Do not run bare `pytest`** when Conda base is active. It often resolves to `/opt/anaconda3/bin/pytest`, which auto-loads LangSmith’s plugin and fails on Python 3.12 before any project tests run.

Check which executable you are using:

```bash
which pytest    # should be .venv/bin/pytest, not anaconda3
```

Any of these are safe:

```bash
make test
bcs-pytest -v
./scripts/test.sh -v
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -v
python -m pytest --disable-plugin-autoload -v
```

After `pip install -r requirements-dev.txt`, prefer **`make test`** or **`bcs-pytest`** over typing `pytest` alone.

## Streamlit UI

```bash
pip install -r requirements-ui.txt
bcs-ui
```

Or:

```bash
streamlit run bus_charging_scheduler/ui/app.py
```

The UI provides a scenario dropdown, YAML viewer, per-bus timetables, and per-station charging/utilization tables.