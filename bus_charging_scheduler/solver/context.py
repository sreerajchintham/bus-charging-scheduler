"""Shared state passed to constraint plugins."""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.network.graph import RouteGraph
from bus_charging_scheduler.solver.variables import BusScheduleVars


@dataclass
class SchedulingContext:
    scenario: Scenario
    graph: RouteGraph
    model: cp_model.CpModel
    horizon_slots: int
    slot_minutes: int
    energy_scale: int
    bus_vars: dict[str, BusScheduleVars] = field(default_factory=dict)
