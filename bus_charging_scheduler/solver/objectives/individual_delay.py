"""Minimize per-bus schedule delay beyond minimum route driving time."""

from __future__ import annotations

from ortools.sat.python import cp_model

from bus_charging_scheduler.solver.context import SchedulingContext
from bus_charging_scheduler.solver.time_grid import minutes_to_slots


def build_expression(context: SchedulingContext) -> cp_model.LinearExpr:
    delay_terms: list[cp_model.LinearExpr] = []
    for bus_vars in context.bus_vars.values():
        minimum_travel_slots = sum(
            minutes_to_slots(leg.travel_minutes, context.slot_minutes)
            for leg in bus_vars.legs
        )
        completion = bus_vars.departure_slots[-1]
        delay_terms.append(completion - minimum_travel_slots)

    if not delay_terms:
        return 0
    return sum(delay_terms)
