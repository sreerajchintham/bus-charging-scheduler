"""Route graph abstraction for station-to-station travel."""

from __future__ import annotations

from dataclasses import dataclass

from bus_charging_scheduler.network.stations import StationIndex


@dataclass(frozen=True)
class RouteEdge:
    from_station_id: str
    to_station_id: str
    distance_km: float
    travel_minutes: float


class RouteGraph:
    """Directed graph of station legs with precomputed travel times."""

    def __init__(
        self,
        station_index: StationIndex,
        edges: dict[tuple[str, str], RouteEdge],
        route_legs: dict[str, list[RouteEdge]],
    ) -> None:
        self.station_index = station_index
        self._edges = edges
        self._route_legs = route_legs

    def travel_minutes(self, from_station_id: str, to_station_id: str) -> float:
        edge = self._edges.get((from_station_id, to_station_id))
        if edge is None:
            raise KeyError(
                f"no edge from {from_station_id!r} to {to_station_id!r}"
            )
        return edge.travel_minutes

    def get_edge(self, from_station_id: str, to_station_id: str) -> RouteEdge:
        return self._edges[(from_station_id, to_station_id)]

    def neighbors_from(self, station_id: str) -> list[RouteEdge]:
        return [
            edge
            for (from_id, _), edge in sorted(self._edges.items())
            if from_id == station_id
        ]

    def leg_sequence_for_route(self, route_id: str) -> list[RouteEdge]:
        try:
            return list(self._route_legs[route_id])
        except KeyError as exc:
            raise KeyError(f"unknown route_id: {route_id!r}") from exc

    def route_ids(self) -> list[str]:
        return sorted(self._route_legs)

    def edges(self) -> list[RouteEdge]:
        return [self._edges[key] for key in sorted(self._edges)]
