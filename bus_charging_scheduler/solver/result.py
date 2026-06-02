"""Solver output models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChargingSession:
    bus_id: str
    station_id: str
    visit_index: int
    start_slot: int
    duration_slots: int
    end_slot: int


@dataclass(frozen=True)
class SolverResult:
    status_name: str
    horizon_slots: int
    slot_minutes: int
    charging_sessions: list[ChargingSession]
    bus_departure_slots: dict[str, list[int]]
