"""Station charger capacity via cumulative constraints on charging intervals."""

from __future__ import annotations

from collections import defaultdict

from bus_charging_scheduler.solver.context import SchedulingContext


def apply(context: SchedulingContext) -> None:
    model = context.model
    intervals_by_station: dict[str, list] = defaultdict(list)

    for bus_vars in context.bus_vars.values():
        for visit_index, station_id in enumerate(bus_vars.station_ids):
            intervals_by_station[station_id].append(
                bus_vars.charge_intervals[visit_index]
            )

    for station in context.graph.station_index:
        intervals = intervals_by_station[station.id]
        if not intervals:
            continue
        model.AddCumulative(intervals, [1] * len(intervals), station.charger_count)
