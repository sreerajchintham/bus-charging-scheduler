"""Minimize total charging time across the network."""

from __future__ import annotations

from ortools.sat.python import cp_model

from bus_charging_scheduler.solver.context import SchedulingContext


def build_expression(context: SchedulingContext) -> cp_model.LinearExpr:
    charge_terms: list[cp_model.IntVar] = []
    for bus_vars in context.bus_vars.values():
        charge_terms.extend(bus_vars.charge_duration_slots)

    if not charge_terms:
        return 0
    return sum(charge_terms)
