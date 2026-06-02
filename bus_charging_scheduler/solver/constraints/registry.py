"""Pluggable constraint registration for the CP-SAT model."""

from __future__ import annotations

from collections.abc import Callable

from bus_charging_scheduler.solver.constraints import (
    battery_range,
    charger_capacity,
    route_order,
)
from bus_charging_scheduler.solver.context import SchedulingContext

ConstraintFunc = Callable[[SchedulingContext], None]


class ConstraintRegistry:
    def __init__(self) -> None:
        self._constraints: list[ConstraintFunc] = []

    def register(self, constraint: ConstraintFunc) -> None:
        self._constraints.append(constraint)

    def apply_all(self, context: SchedulingContext) -> None:
        for constraint in self._constraints:
            constraint(context)


def default_constraint_registry() -> ConstraintRegistry:
    registry = ConstraintRegistry()
    registry.register(route_order.apply)
    registry.register(charger_capacity.apply)
    registry.register(battery_range.apply)
    return registry
