"""Route leg ordering and dwell/charge timing constraints."""

from __future__ import annotations

from bus_charging_scheduler.solver.context import SchedulingContext
from bus_charging_scheduler.solver.time_grid import minutes_to_slots


def apply(context: SchedulingContext) -> None:
    model = context.model
    for bus_vars in context.bus_vars.values():
        for visit_index, leg in enumerate(bus_vars.legs):
            travel_slots = minutes_to_slots(leg.travel_minutes, context.slot_minutes)
            model.Add(
                bus_vars.departure_slots[visit_index] + travel_slots
                == bus_vars.arrival_slots[visit_index + 1]
            )

        for visit_index in range(bus_vars.visit_count):
            model.Add(
                bus_vars.departure_slots[visit_index]
                == bus_vars.arrival_slots[visit_index]
                + bus_vars.charge_duration_slots[visit_index]
            )
