"""CP-SAT scheduler entry point."""

from __future__ import annotations

from ortools.sat.python import cp_model

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.network import build_route_graph
from bus_charging_scheduler.solver.constraints.registry import (
    ConstraintRegistry,
    default_constraint_registry,
)
from bus_charging_scheduler.solver.errors import SolverError
from bus_charging_scheduler.solver.model_builder import build_scheduling_context
from bus_charging_scheduler.solver.objectives.registry import (
    ObjectiveRegistry,
    default_objective_registry,
)
from bus_charging_scheduler.solver.result import ChargingSession, SolverResult


def solve_scenario(
    scenario: Scenario,
    *,
    constraint_registry: ConstraintRegistry | None = None,
    objective_registry: ObjectiveRegistry | None = None,
    max_time_seconds: float = 10.0,
) -> SolverResult:
    graph = build_route_graph(scenario)
    model = cp_model.CpModel()
    context = build_scheduling_context(scenario, graph, model)

    constraints = constraint_registry or default_constraint_registry()
    constraints.apply_all(context)

    objectives = objective_registry or default_objective_registry()
    objectives.apply(context)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_seconds
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)

    status_name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise SolverError(f"solver finished with status {status_name}")

    return _extract_result(context, solver, status_name)


def _extract_result(context, solver: cp_model.CpSolver, status_name: str) -> SolverResult:
    charging_sessions: list[ChargingSession] = []
    bus_arrival_slots: dict[str, list[int]] = {}
    bus_departure_slots: dict[str, list[int]] = {}
    bus_charge_duration_slots: dict[str, list[int]] = {}

    for bus_id, bus_vars in context.bus_vars.items():
        bus_arrival_slots[bus_id] = [
            solver.Value(slot) for slot in bus_vars.arrival_slots
        ]
        bus_departure_slots[bus_id] = [
            solver.Value(slot) for slot in bus_vars.departure_slots
        ]
        bus_charge_duration_slots[bus_id] = [
            solver.Value(slot) for slot in bus_vars.charge_duration_slots
        ]

        for visit_index, station_id in enumerate(bus_vars.station_ids):
            duration = solver.Value(bus_vars.charge_duration_slots[visit_index])
            if duration <= 0:
                continue
            start = solver.Value(bus_vars.arrival_slots[visit_index])
            charging_sessions.append(
                ChargingSession(
                    bus_id=bus_id,
                    station_id=station_id,
                    visit_index=visit_index,
                    start_slot=start,
                    duration_slots=duration,
                    end_slot=start + duration,
                )
            )

    return SolverResult(
        status_name=status_name,
        horizon_slots=context.horizon_slots,
        slot_minutes=context.slot_minutes,
        charging_sessions=charging_sessions,
        bus_arrival_slots=bus_arrival_slots,
        bus_departure_slots=bus_departure_slots,
        bus_charge_duration_slots=bus_charge_duration_slots,
    )
