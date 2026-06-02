# bus-charging-scheduler

Production-oriented **electric bus charging scheduler** built with Python, [OR-Tools CP-SAT](https://developers.google.com/optimization), and Streamlit. Fleets are described entirely in **YAML scenarios**; scheduling rules and objectives plug in through **registries** (no hardcoded stations, routes, or operators).

## Features

- Scenario-driven configuration (`operators`, `stations`, `routes`, `buses`, weights)
- Route graph and travel-time derivation from distance + speed
- CP-SAT model with charging intervals, charger capacity, and battery range
- Weighted objectives: individual delay, operator fairness, network efficiency
- Per-bus timetables and per-station charging orders
- Streamlit UI for exploration and solving

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-ui.txt
make test
bcs-ui
```

## Project structure

```
bus_charging_scheduler/
  domain/          # Pydantic scenario models
  scenarios/       # YAML load + validation
  network/         # Route graph, travel times, stations
  solver/          # CP-SAT model, constraints, objectives
  output/          # Schedule / timetable builder
  ui/              # Streamlit app
data/scenarios/    # Fleet YAML files
docs/              # Architecture and extension guides
tests/
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — layers, CP-SAT model, registries, data flow
- [Extending](docs/EXTENDING.md) — new scenarios, stations, constraints, objectives, multi-charger setups

## Example scenarios

| File | Purpose |
|------|---------|
| `minimal_valid.yaml` | Single bus, round trip (baseline) |
| `three_station_loop.yaml` | Route with an intermediate transfer station |
| `multi_charger_hub.yaml` | Central hub with 4 chargers, 3 buses |
| `two_operators_fairness.yaml` | Two operators, fairness-weighted schedule |

Add a file under `data/scenarios/` and it appears in the UI dropdown after reload.

## Python API

```python
from bus_charging_scheduler.scenarios.loader import load_scenario
from bus_charging_scheduler.output import solve_and_build_schedule

scenario = load_scenario("data/scenarios/minimal_valid.yaml")
result, schedule = solve_and_build_schedule(scenario)
```

Custom registries:

```python
from bus_charging_scheduler.solver import solve_scenario
from bus_charging_scheduler.solver.constraints.registry import default_constraint_registry

registry = default_constraint_registry()
# registry.register(my_constraint.apply)
solve_scenario(scenario, constraint_registry=registry)
```

## Development

```bash
pip install -r requirements-dev.txt
make install
make test
```

### Running tests (Conda users)

Do not run bare `pytest` when Conda base is active — LangSmith’s plugin can crash before tests start. Use:

```bash
make test
# or: bcs-pytest -v
```

## Streamlit UI

```bash
pip install -r requirements-ui.txt
bcs-ui
```

Equivalent: `streamlit run bus_charging_scheduler/ui/app.py`

## Dependencies

| File | Use |
|------|-----|
| `requirements.txt` | Runtime (OR-Tools, Pydantic, PyYAML) |
| `requirements-dev.txt` | Development + pytest |
| `requirements-ui.txt` | Runtime + Streamlit |

`pyproject.toml` remains the packaging source of truth.

## License

See repository defaults; adjust as needed for your deployment.
