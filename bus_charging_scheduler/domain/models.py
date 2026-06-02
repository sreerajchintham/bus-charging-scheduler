"""Domain models for scenario-driven bus charging scheduling."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator


class Operator(BaseModel):
    id: str = Field(min_length=1)
    display_name: str | None = None


class Station(BaseModel):
    id: str = Field(min_length=1)
    charger_count: int = Field(ge=1)


class RouteSegment(BaseModel):
    from_station_id: str = Field(min_length=1)
    to_station_id: str = Field(min_length=1)
    distance_km: float = Field(gt=0)


class Route(BaseModel):
    id: str = Field(min_length=1)
    segments: list[RouteSegment] = Field(min_length=1)


class Bus(BaseModel):
    id: str = Field(min_length=1)
    operator_id: str = Field(min_length=1)
    route_id: str = Field(min_length=1)
    battery_capacity_kwh: float = Field(gt=0)
    initial_soc_kwh: float | None = None
    min_departure_soc_kwh: float | None = None


class ObjectiveWeights(BaseModel):
    individual_delay: float = Field(ge=0)
    operator_fairness: float = Field(ge=0)
    network_efficiency: float = Field(ge=0)


class SchedulingParams(BaseModel):
    horizon_minutes: int = Field(gt=0)
    time_slot_minutes: int = Field(gt=0)


class TravelParams(BaseModel):
    """Network-wide assumptions for converting segment distance to travel time."""

    average_speed_kmh: float = Field(gt=0)


class EnergyParams(BaseModel):
    """Battery consumption and charging rates for range constraints."""

    consumption_kwh_per_km: float = Field(gt=0)
    charging_kwh_per_minute: float = Field(gt=0)


class Scenario(BaseModel):
    name: str = Field(min_length=1)
    operators: list[Operator] = Field(min_length=1)
    stations: list[Station] = Field(min_length=1)
    routes: list[Route] = Field(min_length=1)
    buses: list[Bus] = Field(min_length=1)
    weights: ObjectiveWeights
    scheduling: SchedulingParams
    travel: TravelParams
    energy: EnergyParams

    @field_validator("operators", "stations", "routes", "buses", mode="after")
    @classmethod
    def _non_empty_collections(cls, value: list) -> list:
        if not value:
            raise ValueError("must contain at least one item")
        return value

    @model_validator(mode="after")
    def _apply_bus_soc_defaults(self) -> Scenario:
        buses = [
            bus.model_copy(
                update={
                    "initial_soc_kwh": (
                        bus.initial_soc_kwh
                        if bus.initial_soc_kwh is not None
                        else bus.battery_capacity_kwh
                    ),
                    "min_departure_soc_kwh": (
                        bus.min_departure_soc_kwh
                        if bus.min_departure_soc_kwh is not None
                        else 0.0
                    ),
                }
            )
            for bus in self.buses
        ]
        return self.model_copy(update={"buses": buses})
