"""Create decision variables for a scheduling problem."""

from __future__ import annotations

from ortools.sat.python import cp_model

from bus_charging_scheduler.domain.models import Bus, Scenario
from bus_charging_scheduler.network.graph import RouteGraph
from bus_charging_scheduler.solver.context import SchedulingContext
from bus_charging_scheduler.solver.time_grid import horizon_slots
from bus_charging_scheduler.solver.variables import BusScheduleVars

ENERGY_SCALE = 10


def build_scheduling_context(
    scenario: Scenario,
    graph: RouteGraph,
    model: cp_model.CpModel,
) -> SchedulingContext:
    slot_minutes = scenario.scheduling.time_slot_minutes
    horizon = horizon_slots(
        scenario.scheduling.horizon_minutes,
        slot_minutes,
    )

    context = SchedulingContext(
        scenario=scenario,
        graph=graph,
        model=model,
        horizon_slots=horizon,
        slot_minutes=slot_minutes,
        energy_scale=ENERGY_SCALE,
    )

    for bus in scenario.buses:
        context.bus_vars[bus.id] = _create_bus_variables(context, bus)

    return context


def _create_bus_variables(
    context: SchedulingContext,
    bus: Bus,
) -> BusScheduleVars:
    model = context.model
    horizon = context.horizon_slots
    legs = context.graph.leg_sequence_for_route(bus.route_id)
    station_ids = [legs[0].from_station_id] + [leg.to_station_id for leg in legs]
    visit_count = len(station_ids)

    arrival_slots = [
        model.NewIntVar(0, horizon, f"arrival_{bus.id}_{index}")
        for index in range(visit_count)
    ]
    departure_slots = [
        model.NewIntVar(0, horizon, f"departure_{bus.id}_{index}")
        for index in range(visit_count)
    ]
    charge_duration_slots = [
        model.NewIntVar(0, horizon, f"charge_duration_{bus.id}_{index}")
        for index in range(visit_count)
    ]
    charge_intervals = [
        model.NewIntervalVar(
            arrival_slots[index],
            charge_duration_slots[index],
            departure_slots[index],
            f"charge_interval_{bus.id}_{index}",
        )
        for index in range(visit_count)
    ]

    max_soc_deci = int(round(bus.battery_capacity_kwh * context.energy_scale))
    soc_at_departure_deci_kwh = [
        model.NewIntVar(0, max_soc_deci, f"soc_departure_{bus.id}_{index}")
        for index in range(visit_count)
    ]

    model.Add(arrival_slots[0] == 0)

    return BusScheduleVars(
        bus=bus,
        station_ids=station_ids,
        legs=legs,
        arrival_slots=arrival_slots,
        departure_slots=departure_slots,
        charge_duration_slots=charge_duration_slots,
        charge_intervals=charge_intervals,
        soc_at_departure_deci_kwh=soc_at_departure_deci_kwh,
    )
