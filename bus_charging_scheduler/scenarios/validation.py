"""Cross-field semantic validation for scenarios."""

from __future__ import annotations

from bus_charging_scheduler.domain.models import Scenario


def _collect_duplicate_ids(ids: list[str], label: str) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for entity_id in ids:
        if entity_id in seen:
            errors.append(f"duplicate {label} id: {entity_id!r}")
        seen.add(entity_id)
    return errors


def validate_scenario(scenario: Scenario) -> list[str]:
    """Return human-readable validation errors; empty list means valid."""
    errors: list[str] = []

    errors.extend(
        _collect_duplicate_ids([o.id for o in scenario.operators], "operator")
    )
    errors.extend(
        _collect_duplicate_ids([s.id for s in scenario.stations], "station")
    )
    errors.extend(_collect_duplicate_ids([r.id for r in scenario.routes], "route"))
    errors.extend(_collect_duplicate_ids([b.id for b in scenario.buses], "bus"))

    operator_ids = {o.id for o in scenario.operators}
    station_ids = {s.id for s in scenario.stations}
    route_ids = {r.id for r in scenario.routes}

    for bus in scenario.buses:
        if bus.operator_id not in operator_ids:
            errors.append(
                f"bus {bus.id!r}: unknown operator_id {bus.operator_id!r}"
            )
        if bus.route_id not in route_ids:
            errors.append(f"bus {bus.id!r}: unknown route_id {bus.route_id!r}")

        assert bus.initial_soc_kwh is not None
        assert bus.min_departure_soc_kwh is not None

        if bus.initial_soc_kwh > bus.battery_capacity_kwh:
            errors.append(
                f"bus {bus.id!r}: initial_soc_kwh ({bus.initial_soc_kwh}) "
                f"exceeds battery_capacity_kwh ({bus.battery_capacity_kwh})"
            )
        if bus.min_departure_soc_kwh > bus.battery_capacity_kwh:
            errors.append(
                f"bus {bus.id!r}: min_departure_soc_kwh ({bus.min_departure_soc_kwh}) "
                f"exceeds battery_capacity_kwh ({bus.battery_capacity_kwh})"
            )
        if bus.min_departure_soc_kwh > bus.initial_soc_kwh:
            errors.append(
                f"bus {bus.id!r}: min_departure_soc_kwh ({bus.min_departure_soc_kwh}) "
                f"exceeds initial_soc_kwh ({bus.initial_soc_kwh})"
            )

    for route in scenario.routes:
        for index, segment in enumerate(route.segments):
            if segment.from_station_id not in station_ids:
                errors.append(
                    f"route {route.id!r} segment {index}: "
                    f"unknown from_station_id {segment.from_station_id!r}"
                )
            if segment.to_station_id not in station_ids:
                errors.append(
                    f"route {route.id!r} segment {index}: "
                    f"unknown to_station_id {segment.to_station_id!r}"
                )

    horizon = scenario.scheduling.horizon_minutes
    slot = scenario.scheduling.time_slot_minutes
    if horizon % slot != 0:
        errors.append(
            f"scheduling.horizon_minutes ({horizon}) must be divisible by "
            f"time_slot_minutes ({slot})"
        )

    return errors
