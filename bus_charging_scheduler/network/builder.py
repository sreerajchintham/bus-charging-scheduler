"""Build network abstractions from a validated scenario."""

from __future__ import annotations

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.network.errors import NetworkBuildError
from bus_charging_scheduler.network.graph import RouteEdge, RouteGraph
from bus_charging_scheduler.network.stations import StationIndex
from bus_charging_scheduler.network.travel import TravelCalculator


def build_route_graph(scenario: Scenario) -> RouteGraph:
    """Construct station index, edges, and per-route leg sequences."""
    travel = TravelCalculator(scenario.travel.average_speed_kmh)
    station_index = StationIndex(scenario.stations)
    edges: dict[tuple[str, str], RouteEdge] = {}
    route_legs: dict[str, list[RouteEdge]] = {}

    for route in scenario.routes:
        legs: list[RouteEdge] = []
        for segment in route.segments:
            key = (segment.from_station_id, segment.to_station_id)
            travel_minutes = travel.minutes_for_distance(segment.distance_km)
            edge = RouteEdge(
                from_station_id=segment.from_station_id,
                to_station_id=segment.to_station_id,
                distance_km=segment.distance_km,
                travel_minutes=travel_minutes,
            )

            existing = edges.get(key)
            if existing is not None and existing.distance_km != segment.distance_km:
                raise NetworkBuildError(
                    f"conflicting distance for edge {key[0]!r} -> {key[1]!r}: "
                    f"{existing.distance_km} km vs {segment.distance_km} km"
                )
            edges[key] = edge
            legs.append(edge)

        route_legs[route.id] = legs

    return RouteGraph(station_index=station_index, edges=edges, route_legs=route_legs)
