"""Battery state-of-charge limits along each route."""

from __future__ import annotations

from bus_charging_scheduler.solver.context import SchedulingContext


def apply(context: SchedulingContext) -> None:
    model = context.model
    consumption = context.scenario.energy.consumption_kwh_per_km
    charge_per_slot = int(
        round(
            context.scenario.energy.charging_kwh_per_minute
            * context.slot_minutes
            * context.energy_scale
        )
    )

    for bus_vars in context.bus_vars.values():
        bus = bus_vars.bus
        initial_deci = int(round(bus.initial_soc_kwh * context.energy_scale))
        min_departure_deci = int(
            round(bus.min_departure_soc_kwh * context.energy_scale)
        )
        capacity_deci = int(round(bus.battery_capacity_kwh * context.energy_scale))

        soc = bus_vars.soc_at_departure_deci_kwh
        charge = bus_vars.charge_duration_slots

        model.Add(soc[0] == initial_deci + charge_per_slot * charge[0])
        model.Add(soc[0] >= min_departure_deci)
        model.Add(soc[0] <= capacity_deci)

        for visit_index, leg in enumerate(bus_vars.legs):
            leg_energy_deci = int(
                round(leg.distance_km * consumption * context.energy_scale)
            )
            next_soc = soc[visit_index + 1]
            model.Add(
                next_soc
                == soc[visit_index] - leg_energy_deci + charge_per_slot * charge[visit_index + 1]
            )
            model.Add(soc[visit_index] >= leg_energy_deci)
            model.Add(next_soc >= min_departure_deci)
            model.Add(next_soc <= capacity_deci)
