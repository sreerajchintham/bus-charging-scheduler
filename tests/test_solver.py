import copy

import pytest

from bus_charging_scheduler.scenarios.loader import load_scenario_from_dict
from bus_charging_scheduler.solver import SolverError, solve_scenario
from tests.conftest import MINIMAL_SCENARIO_PATH, minimal_scenario_dict


def test_solve_minimal_scenario_from_disk():
    from bus_charging_scheduler.scenarios.loader import load_scenario

    scenario = load_scenario(MINIMAL_SCENARIO_PATH)
    result = solve_scenario(scenario)

    assert result.status_name in {"OPTIMAL", "FEASIBLE"}
    assert result.bus_departure_slots["bus-01"][-1] > 0


def test_solve_minimal_scenario_dict(minimal_scenario):
    result = solve_scenario(minimal_scenario)
    assert result.status_name in {"OPTIMAL", "FEASIBLE"}


def test_route_order_respected(minimal_scenario):
    result = solve_scenario(minimal_scenario)
    # Two legs at 18.75 min -> 2 slots each (15-min slots) = 4 slots travel; plus dwell.
    final_departure_slot = result.bus_departure_slots["bus-01"][-1]
    assert final_departure_slot >= 4


def test_infeasible_when_battery_cannot_support_route():
    data = minimal_scenario_dict()
    data["buses"][0]["initial_soc_kwh"] = 10
    data["buses"][0]["min_departure_soc_kwh"] = 10
    data["energy"]["charging_kwh_per_minute"] = 0.01
    scenario = load_scenario_from_dict(data)

    with pytest.raises(SolverError):
        solve_scenario(scenario, max_time_seconds=2.0)


def test_charger_capacity_infeasible_with_overlapping_sessions():
    data = minimal_scenario_dict()
    data["stations"][0]["charger_count"] = 1
    data["buses"].append(
        {
            "id": "bus-02",
            "operator_id": "op-north",
            "route_id": "run-101",
            "battery_capacity_kwh": 350,
            "initial_soc_kwh": 50,
            "min_departure_soc_kwh": 250,
        }
    )
    data["buses"][0]["initial_soc_kwh"] = 50
    data["buses"][0]["min_departure_soc_kwh"] = 250
    scenario = load_scenario_from_dict(data)

    with pytest.raises(SolverError):
        solve_scenario(scenario, max_time_seconds=2.0)
