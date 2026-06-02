"""Station lookup abstraction."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from bus_charging_scheduler.domain.models import Station


class StationIndex:
    """Immutable index of stations by id."""

    def __init__(self, stations: Iterable[Station]) -> None:
        self._stations: dict[str, Station] = {station.id: station for station in stations}

    def get(self, station_id: str) -> Station:
        try:
            return self._stations[station_id]
        except KeyError as exc:
            raise KeyError(f"unknown station_id: {station_id!r}") from exc

    def __contains__(self, station_id: str) -> bool:
        return station_id in self._stations

    def __len__(self) -> int:
        return len(self._stations)

    def ids(self) -> list[str]:
        return sorted(self._stations)

    def __iter__(self) -> Iterator[Station]:
        return iter(self._stations.values())
