# Extending the scheduler

This guide shows how to extend the system without forking core logic: new YAML scenarios, stations, constraints (“rules”), and objectives.

## Add a new scenario

1. Create `data/scenarios/my_fleet.yaml` (copy `minimal_valid.yaml` as a template).  
2. Define unique `id` fields for operators, stations, routes, and buses.  
3. Ensure segment `from_station_id` / `to_station_id` reference defined stations.  
4. Run validation: `load_scenario("data/scenarios/my_fleet.yaml")`.  
5. Open **bcs-ui** — the file appears in the scenario dropdown automatically.

Required top-level keys: `name`, `operators`, `stations`, `routes`, `buses`, `weights`, `scheduling`, `travel`, `energy`.

## Add a new station

Stations are data-only:

```yaml
stations:
  - id: hub-west
    charger_count: 3
```

Reference the station in route segments:

```yaml
routes:
  - id: express-1
    segments:
      - from_station_id: depot-a
        to_station_id: hub-west
        distance_km: 6.0
```

`charger_count` drives the cumulative capacity constraint in `charger_capacity.py`. Use `multi_charger_hub.yaml` as a reference for high-capacity hubs.

## Add a new constraint (rule)

1. Create `bus_charging_scheduler/solver/constraints/my_rule.py`:

```python
from bus_charging_scheduler.solver.context import SchedulingContext


def apply(context: SchedulingContext) -> None:
    model = context.model
    # Example: buses must not depart before slot 4
    for bus_vars in context.bus_vars.values():
        model.Add(bus_vars.departure_slots[0] >= 4)
```

2. Register it:

```python
from bus_charging_scheduler.solver.constraints.registry import default_constraint_registry
from bus_charging_scheduler.solver.constraints import my_rule

registry = default_constraint_registry()
registry.register(my_rule.apply)

solve_scenario(scenario, constraint_registry=registry)
```

3. Add tests under `tests/` that build a small scenario and assert feasibility or infeasibility.

Keep rules **linear** over existing integer variables when possible so CP-SAT remains efficient.

## Add a new objective

1. Create `bus_charging_scheduler/solver/objectives/my_objective.py` with `build_expression(context) -> LinearExpr`.  
2. Add a weight field to `ObjectiveWeights` in `domain/models.py` and scenario YAML (migration for existing files).  
3. Register in `objectives/registry.py` or pass a custom `ObjectiveRegistry` at solve time.  

See `network_efficiency.py` for a simple sum-of-variables objective.

## Scenario-only policy tuning

Objective weights require no code changes:

```yaml
weights:
  individual_delay: 1.0
  operator_fairness: 2.0
  network_efficiency: 0.5
```

At least one weight must be &gt; 0. Set others to `0` to disable that term.

## Multi-charger fleets

Model capacity per station, not globally:

```yaml
stations:
  - id: hub-central
    charger_count: 4
  - id: satellite-depot
    charger_count: 1
```

When many buses share a low-capacity station, the solver staggers charging intervals. If the model is **INFEASIBLE**, relax `min_departure_soc_kwh`, increase `charger_count`, or extend `horizon_minutes`.

## Tests and quality

- Unit-test loaders and network code without the solver when possible.  
- Solver tests: use `make test` (`num_search_workers = 1` for portability).  
- Add parametrized tests for new YAML files (see `tests/test_example_scenarios.py`).
