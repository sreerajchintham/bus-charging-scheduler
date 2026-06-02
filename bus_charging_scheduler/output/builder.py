"""Build human-readable schedules from solver output."""

from __future__ import annotations

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.network.graph import RouteGraph
from bus_charging_scheduler.network import build_route_graph
from bus_charging_scheduler.output.models import (
    BusTimetable,
    BusVisit,
    Schedule,
    StationChargingEntry,
    StationChargingOrder,
)
from bus_charging_scheduler.solver.result import SolverResult


def _slot_to_minutes(slot: int, slot_minutes: int) -> int:
    return slot * slot_minutes


def build_schedule(
    scenario: Scenario,
    result: SolverResult,
    graph: RouteGraph | None = None,
) -> Schedule:
    route_graph = graph or build_route_graph(scenario)
    slot_minutes = result.slot_minutes

    bus_timetables = [
        _build_bus_timetable(scenario, result, route_graph, bus.id)
        for bus in scenario.buses
    ]
    station_charging_orders = _build_station_charging_orders(scenario, result)

    return Schedule(
        scenario_name=scenario.name,
        status_name=result.status_name,
        slot_minutes=slot_minutes,
        bus_timetables=sorted(bus_timetables, key=lambda table: table.bus_id),
        station_charging_orders=sorted(
            station_charging_orders, key=lambda order: order.station_id
        ),
    )


def _build_bus_timetable(
    scenario: Scenario,
    result: SolverResult,
    graph: RouteGraph,
    bus_id: str,
) -> BusTimetable:
    bus = next(bus for bus in scenario.buses if bus.id == bus_id)
    legs = graph.leg_sequence_for_route(bus.route_id)
    station_ids = [legs[0].from_station_id] + [leg.to_station_id for leg in legs]

    arrivals = result.bus_arrival_slots[bus_id]
    departures = result.bus_departure_slots[bus_id]
    charge_slots = result.bus_charge_duration_slots[bus_id]

    visits: list[BusVisit] = []
    for visit_index, station_id in enumerate(station_ids):
        leg_to = legs[visit_index].to_station_id if visit_index < len(legs) else None
        visits.append(
            BusVisit(
                visit_index=visit_index,
                station_id=station_id,
                arrival_minutes=_slot_to_minutes(arrivals[visit_index], result.slot_minutes),
                departure_minutes=_slot_to_minutes(
                    departures[visit_index], result.slot_minutes
                ),
                charge_minutes=_slot_to_minutes(
                    charge_slots[visit_index], result.slot_minutes
                ),
                leg_to_station_id=leg_to,
            )
        )

    return BusTimetable(
        bus_id=bus.id,
        operator_id=bus.operator_id,
        route_id=bus.route_id,
        visits=visits,
    )


def _build_station_charging_orders(
    scenario: Scenario,
    result: SolverResult,
) -> list[StationChargingOrder]:
    sessions_by_station: dict[str, list[StationChargingEntry]] = {
        station.id: [] for station in scenario.stations
    }

    for session in result.charging_sessions:
        sessions_by_station[session.station_id].append(
            StationChargingEntry(
                rank=0,
                bus_id=session.bus_id,
                start_minutes=_slot_to_minutes(
                    session.start_slot, result.slot_minutes
                ),
                end_minutes=_slot_to_minutes(session.end_slot, result.slot_minutes),
                duration_minutes=_slot_to_minutes(
                    session.duration_slots, result.slot_minutes
                ),
            )
        )

    orders: list[StationChargingOrder] = []
    for station in scenario.stations:
        sorted_sessions = sorted(
            sessions_by_station[station.id],
            key=lambda entry: (entry.start_minutes, entry.bus_id),
        )
        ranked_sessions = [
            StationChargingEntry(
                rank=index + 1,
                bus_id=entry.bus_id,
                start_minutes=entry.start_minutes,
                end_minutes=entry.end_minutes,
                duration_minutes=entry.duration_minutes,
            )
            for index, entry in enumerate(sorted_sessions)
        ]
        orders.append(
            StationChargingOrder(
                station_id=station.id,
                charger_count=station.charger_count,
                sessions=ranked_sessions,
            )
        )

    return orders
