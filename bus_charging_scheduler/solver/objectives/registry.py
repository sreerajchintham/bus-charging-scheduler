"""Weighted objective registry for the CP-SAT model."""

from __future__ import annotations

from collections.abc import Callable

from ortools.sat.python import cp_model

from bus_charging_scheduler.solver.context import SchedulingContext
from bus_charging_scheduler.solver.objectives import (
    individual_delay,
    network_efficiency,
    operator_fairness,
)

ObjectiveFunc = Callable[[SchedulingContext], cp_model.LinearExpr]

WEIGHT_SCALE = 100


class ObjectiveRegistry:
    def __init__(self) -> None:
        self._objectives: list[tuple[str, ObjectiveFunc]] = []

    def register(self, name: str, objective: ObjectiveFunc) -> None:
        self._objectives.append((name, objective))

    def apply(self, context: SchedulingContext) -> None:
        weights = context.scenario.weights
        weight_by_name = {
            "individual_delay": weights.individual_delay,
            "operator_fairness": weights.operator_fairness,
            "network_efficiency": weights.network_efficiency,
        }

        weighted_terms: list[cp_model.LinearExpr] = []
        for name, objective in self._objectives:
            weight = weight_by_name[name]
            if weight <= 0:
                continue
            coefficient = int(round(weight * WEIGHT_SCALE))
            if coefficient == 0:
                continue
            expression = objective(context)
            weighted_terms.append(coefficient * expression)

        if not weighted_terms:
            raise ValueError("at least one objective weight must be positive")

        context.model.Minimize(sum(weighted_terms))


def default_objective_registry() -> ObjectiveRegistry:
    registry = ObjectiveRegistry()
    registry.register("individual_delay", individual_delay.build_expression)
    registry.register("operator_fairness", operator_fairness.build_expression)
    registry.register("network_efficiency", network_efficiency.build_expression)
    return registry
