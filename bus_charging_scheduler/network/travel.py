"""Travel-time calculations from segment distance."""

from __future__ import annotations


class TravelCalculator:
    """Convert road distance to minutes using a scenario-configured average speed."""

    def __init__(self, average_speed_kmh: float) -> None:
        if average_speed_kmh <= 0:
            raise ValueError("average_speed_kmh must be positive")
        self.average_speed_kmh = average_speed_kmh

    def minutes_for_distance(self, distance_km: float) -> float:
        if distance_km <= 0:
            raise ValueError("distance_km must be positive")
        return (distance_km / self.average_speed_kmh) * 60.0
