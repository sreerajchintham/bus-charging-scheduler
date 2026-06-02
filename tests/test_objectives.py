import copy

import pytest

from bus_charging_scheduler.scenarios.loader import load_scenario_from_dict
from bus_charging_scheduler.solver import solve_scenario
from tests.conftest import minimal_scenario_dict


def _two_bus_scenario_dict() -> dict:
    data = copy.deepcopy(minimal_scenario_dict())
    data["routes"].append(
        {
            "id": "run-short",
            "segments": [
                {
                    "from_station_id": "depot-a",
                    "to_station_id": "terminal-b",
                    "distance_km": 12.5,
                }
            ],
        }
    )
    data["buses"].append(
        {
            "id": "bus-02",
            "operator_id": "op-north",
            "route_id": "run-short",
            "battery_capacity_kwh": 350,
            "initial_soc_kwh": 280,
            "min_departure_soc_kwh": 200,
        }
    )
    return data


def test_zero_weights_raises():
    data = minimal_scenario_dict()
    data["weights"] = {
        "individual_delay": 0,
        "operator_fairness": 0,
        "network_efficiency": 0,
    }
    scenario = load_scenario_from_dict(data)
    with pytest.raises(ValueError, match="at least one objective weight"):
        solve_scenario(scenario)


def test_network_efficiency_minimizes_charging_when_optional():
    data = minimal_scenario_dict()
    data["weights"] = {
        "individual_delay": 0,
        "operator_fairness": 0,
        "network_efficiency": 1.0,
    }
    result = solve_scenario(load_scenario_from_dict(data))
    assert result.status_name in {"OPTIMAL", "FEASIBLE"}
    assert sum(session.duration_slots for session in result.charging_sessions) == 0


def test_operator_fairness_reduces_completion_spread():
    data = _two_bus_scenario_dict()
    data["weights"] = {
        "individual_delay": 0,
        "operator_fairness": 10.0,
        "network_efficiency": 0,
    }
    fair_result = solve_scenario(load_scenario_from_dict(data))

    data["weights"] = {
        "individual_delay": 10.0,
        "operator_fairness": 0,
        "network_efficiency": 0,
    }
    delay_result = solve_scenario(load_scenario_from_dict(data))

    fair_times = list(fair_result.bus_departure_slots.values())
    delay_times = list(delay_result.bus_departure_slots.values())
    fair_spread = max(f[-1] for f in fair_times) - min(f[-1] for f in fair_times)
    delay_spread = max(d[-1] for d in delay_times) - min(d[-1] for d in delay_times)
    assert fair_spread <= delay_spread
