"""End-to-end solve and schedule materialization."""

from __future__ import annotations

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.output.builder import build_schedule
from bus_charging_scheduler.output.models import Schedule
from bus_charging_scheduler.solver.result import SolverResult
from bus_charging_scheduler.solver.scheduler import solve_scenario


def solve_and_build_schedule(scenario: Scenario) -> tuple[SolverResult, Schedule]:
    result = solve_scenario(scenario)
    schedule = build_schedule(scenario, result)
    return result, schedule
