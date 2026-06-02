"""Decision variables for bus schedules."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from bus_charging_scheduler.domain.models import Bus
from bus_charging_scheduler.network.graph import RouteEdge


@dataclass
class BusScheduleVars:
    bus: Bus
    station_ids: list[str]
    legs: list[RouteEdge]
    arrival_slots: list[cp_model.IntVar]
    departure_slots: list[cp_model.IntVar]
    charge_duration_slots: list[cp_model.IntVar]
    charge_intervals: list[cp_model.IntervalVar]
    soc_at_departure_deci_kwh: list[cp_model.IntVar]

    @property
    def visit_count(self) -> int:
        return len(self.station_ids)
