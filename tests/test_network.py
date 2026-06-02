import pytest

from bus_charging_scheduler.network import (
    NetworkBuildError,
    TravelCalculator,
    build_route_graph,
)
from bus_charging_scheduler.scenarios.loader import load_scenario
from tests.conftest import MINIMAL_SCENARIO_PATH, minimal_scenario_dict


def test_travel_calculator_minutes():
    travel = TravelCalculator(average_speed_kmh=40)
    # 12.5 km at 40 km/h -> 18.75 minutes
    assert travel.minutes_for_distance(12.5) == pytest.approx(18.75)


def test_build_route_graph_from_fixture(minimal_scenario):
    graph = build_route_graph(minimal_scenario)

    assert len(graph.station_index) == 2
    assert graph.station_index.get("depot-a").charger_count == 2

    legs = graph.leg_sequence_for_route("run-101")
    assert len(legs) == 2
    assert legs[0].travel_minutes == pytest.approx(18.75)
    assert graph.travel_minutes("depot-a", "terminal-b") == pytest.approx(18.75)


def test_route_total_travel_minutes(minimal_scenario):
    graph = build_route_graph(minimal_scenario)
    legs = graph.leg_sequence_for_route("run-101")
    total = sum(leg.travel_minutes for leg in legs)
    assert total == pytest.approx(37.5)


def test_neighbors_from_station(minimal_scenario):
    graph = build_route_graph(minimal_scenario)
    from_depot = graph.neighbors_from("depot-a")
    assert len(from_depot) == 1
    assert from_depot[0].to_station_id == "terminal-b"


def test_conflicting_edge_distance_raises():
    data = minimal_scenario_dict()
    data["routes"].append(
        {
            "id": "run-202",
            "segments": [
                {
                    "from_station_id": "depot-a",
                    "to_station_id": "terminal-b",
                    "distance_km": 20.0,
                }
            ],
        }
    )
    from bus_charging_scheduler.scenarios.loader import load_scenario_from_dict

    scenario = load_scenario_from_dict(data)
    with pytest.raises(NetworkBuildError, match="conflicting distance"):
        build_route_graph(scenario)


def test_unknown_route_raises(minimal_scenario):
    graph = build_route_graph(minimal_scenario)
    with pytest.raises(KeyError, match="unknown route_id"):
        graph.leg_sequence_for_route("missing-route")


def test_load_scenario_and_build_graph_integration():
    scenario = load_scenario(MINIMAL_SCENARIO_PATH)
    graph = build_route_graph(scenario)
    assert graph.travel_minutes("terminal-b", "depot-a") == pytest.approx(18.75)
