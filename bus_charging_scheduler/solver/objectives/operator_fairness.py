"""Minimize completion-time spread between buses of the same operator."""

from __future__ import annotations

from collections import defaultdict

from ortools.sat.python import cp_model

from bus_charging_scheduler.solver.context import SchedulingContext


def build_expression(context: SchedulingContext) -> cp_model.LinearExpr:
    model = context.model
    horizon = context.horizon_slots
    completions_by_operator: dict[str, list[cp_model.IntVar]] = defaultdict(list)

    for bus_vars in context.bus_vars.values():
        completions_by_operator[bus_vars.bus.operator_id].append(
            bus_vars.departure_slots[-1]
        )

    fairness_gaps: list[cp_model.IntVar] = []
    for operator_id, completions in completions_by_operator.items():
        if len(completions) < 2:
            continue

        max_completion = model.NewIntVar(
            0, horizon, f"fairness_max_{operator_id}"
        )
        min_completion = model.NewIntVar(
            0, horizon, f"fairness_min_{operator_id}"
        )
        for completion in completions:
            model.Add(max_completion >= completion)
            model.Add(min_completion <= completion)

        gap = model.NewIntVar(0, horizon, f"fairness_gap_{operator_id}")
        model.Add(gap == max_completion - min_completion)
        fairness_gaps.append(gap)

    if not fairness_gaps:
        return 0
    return sum(fairness_gaps)
