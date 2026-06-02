import copy

import pytest

from bus_charging_scheduler.scenarios.errors import ScenarioValidationError
from bus_charging_scheduler.scenarios.loader import load_scenario, load_scenario_from_dict
from tests.conftest import MINIMAL_SCENARIO_PATH, minimal_scenario_dict


def test_minimal_valid_fixture_loads():
    scenario = load_scenario(MINIMAL_SCENARIO_PATH)
    assert scenario.name == "example-morning-peak"
    assert len(scenario.stations) == 2
    assert scenario.buses[0].initial_soc_kwh == 280


def test_load_from_dict_roundtrip(minimal_scenario_dict_fixture):
    scenario = load_scenario_from_dict(minimal_scenario_dict_fixture)
    assert scenario.name == "test-scenario"
    assert scenario.weights.individual_delay == 1.0
    assert scenario.scheduling.horizon_minutes == 1440


def test_bus_soc_defaults_when_omitted():
    data = minimal_scenario_dict()
    data["buses"] = [
        {
            "id": "bus-02",
            "operator_id": "op-north",
            "route_id": "run-101",
            "battery_capacity_kwh": 400,
        }
    ]
    scenario = load_scenario_from_dict(data)
    bus = scenario.buses[0]
    assert bus.initial_soc_kwh == 400
    assert bus.min_departure_soc_kwh == 0.0


def test_duplicate_station_id_fails():
    data = minimal_scenario_dict()
    data["stations"].append({"id": "depot-a", "charger_count": 1})
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("duplicate station id" in msg for msg in exc_info.value.messages)


def test_bus_unknown_operator_fails():
    data = minimal_scenario_dict()
    data["buses"][0]["operator_id"] = "missing-op"
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("unknown operator_id" in msg for msg in exc_info.value.messages)


def test_segment_unknown_station_fails():
    data = minimal_scenario_dict()
    data["routes"][0]["segments"][0]["from_station_id"] = "unknown-station"
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("unknown from_station_id" in msg for msg in exc_info.value.messages)


def test_invalid_soc_bounds_fails():
    data = minimal_scenario_dict()
    data["buses"][0]["initial_soc_kwh"] = 500
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("initial_soc_kwh" in msg for msg in exc_info.value.messages)


def test_min_departure_exceeds_initial_soc_fails():
    data = minimal_scenario_dict()
    data["buses"][0]["min_departure_soc_kwh"] = 300
    data["buses"][0]["initial_soc_kwh"] = 250
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("min_departure_soc_kwh" in msg for msg in exc_info.value.messages)


def test_horizon_not_divisible_by_slot_fails():
    data = minimal_scenario_dict()
    data["scheduling"]["horizon_minutes"] = 1000
    with pytest.raises(ScenarioValidationError) as exc_info:
        load_scenario_from_dict(data)
    assert any("divisible" in msg for msg in exc_info.value.messages)


@pytest.mark.parametrize(
    "missing_key",
    [
        "name",
        "operators",
        "stations",
        "routes",
        "buses",
        "weights",
        "scheduling",
        "travel",
    ],
)
def test_missing_required_key_fails(missing_key):
    data = copy.deepcopy(minimal_scenario_dict())
    del data[missing_key]
    with pytest.raises(ScenarioValidationError):
        load_scenario_from_dict(data)
