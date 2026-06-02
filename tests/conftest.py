from pathlib import Path

import pytest

from bus_charging_scheduler.scenarios.loader import load_scenario_from_dict

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "data" / "scenarios"
MINIMAL_SCENARIO_PATH = FIXTURES_DIR / "minimal_valid.yaml"


def minimal_scenario_dict() -> dict:
    """Valid scenario payload for unit tests."""
    return {
        "name": "test-scenario",
        "operators": [{"id": "op-north", "display_name": "North Depot"}],
        "stations": [
            {"id": "depot-a", "charger_count": 2},
            {"id": "terminal-b", "charger_count": 1},
        ],
        "routes": [
            {
                "id": "run-101",
                "segments": [
                    {
                        "from_station_id": "depot-a",
                        "to_station_id": "terminal-b",
                        "distance_km": 12.5,
                    },
                    {
                        "from_station_id": "terminal-b",
                        "to_station_id": "depot-a",
                        "distance_km": 12.5,
                    },
                ],
            }
        ],
        "buses": [
            {
                "id": "bus-01",
                "operator_id": "op-north",
                "route_id": "run-101",
                "battery_capacity_kwh": 350,
                "initial_soc_kwh": 280,
                "min_departure_soc_kwh": 200,
            }
        ],
        "weights": {
            "individual_delay": 1.0,
            "operator_fairness": 0.5,
            "network_efficiency": 0.3,
        },
        "scheduling": {
            "horizon_minutes": 1440,
            "time_slot_minutes": 15,
        },
        "travel": {
            "average_speed_kmh": 40,
        },
    }


@pytest.fixture
def minimal_scenario_dict_fixture() -> dict:
    return minimal_scenario_dict()


@pytest.fixture
def minimal_scenario(minimal_scenario_dict_fixture):
    return load_scenario_from_dict(minimal_scenario_dict_fixture)
