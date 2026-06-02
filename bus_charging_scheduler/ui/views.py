"""Convert schedule models to display-friendly rows (no Streamlit dependency)."""

from __future__ import annotations

from bus_charging_scheduler.output.models import BusTimetable, Schedule, StationChargingOrder


def bus_timetable_rows(timetable: BusTimetable) -> list[dict[str, object]]:
    return [
        {
            "visit": visit.visit_index,
            "station": visit.station_id,
            "arrival_min": visit.arrival_minutes,
            "charge_min": visit.charge_minutes,
            "departure_min": visit.departure_minutes,
            "next_station": visit.leg_to_station_id or "",
        }
        for visit in timetable.visits
    ]


def station_utilization_rows(
    order: StationChargingOrder,
    horizon_minutes: int,
) -> dict[str, object]:
    busy_minutes = sum(session.duration_minutes for session in order.sessions)
    capacity_minutes = order.charger_count * horizon_minutes
    utilization_pct = (
        round(100.0 * busy_minutes / capacity_minutes, 1)
        if capacity_minutes > 0
        else 0.0
    )
    return {
        "station": order.station_id,
        "chargers": order.charger_count,
        "sessions": len(order.sessions),
        "busy_min": busy_minutes,
        "utilization_pct": utilization_pct,
    }


def station_charging_rows(order: StationChargingOrder) -> list[dict[str, object]]:
    return [
        {
            "rank": entry.rank,
            "bus": entry.bus_id,
            "start_min": entry.start_minutes,
            "end_min": entry.end_minutes,
            "duration_min": entry.duration_minutes,
        }
        for entry in order.sessions
    ]


def schedule_horizon_minutes(schedule: Schedule) -> int:
    max_minute = 0
    for timetable in schedule.bus_timetables:
        for visit in timetable.visits:
            max_minute = max(max_minute, visit.departure_minutes)
    for order in schedule.station_charging_orders:
        for session in order.sessions:
            max_minute = max(max_minute, session.end_minutes)
    return max_minute
