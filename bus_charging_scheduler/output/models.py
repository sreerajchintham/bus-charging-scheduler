"""Structured schedule output for buses and stations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BusVisit:
    visit_index: int
    station_id: str
    arrival_minutes: int
    departure_minutes: int
    charge_minutes: int
    leg_to_station_id: str | None


@dataclass(frozen=True)
class BusTimetable:
    bus_id: str
    operator_id: str
    route_id: str
    visits: list[BusVisit]


@dataclass(frozen=True)
class StationChargingEntry:
    rank: int
    bus_id: str
    start_minutes: int
    end_minutes: int
    duration_minutes: int


@dataclass(frozen=True)
class StationChargingOrder:
    station_id: str
    charger_count: int
    sessions: list[StationChargingEntry]


@dataclass(frozen=True)
class Schedule:
    scenario_name: str
    status_name: str
    slot_minutes: int
    bus_timetables: list[BusTimetable]
    station_charging_orders: list[StationChargingOrder]
