"""Time discretization helpers."""

from __future__ import annotations

import math


def minutes_to_slots(minutes: float, slot_minutes: int) -> int:
    if slot_minutes <= 0:
        raise ValueError("slot_minutes must be positive")
    return int(math.ceil(minutes / slot_minutes))


def horizon_slots(horizon_minutes: int, slot_minutes: int) -> int:
    if horizon_minutes % slot_minutes != 0:
        raise ValueError("horizon_minutes must be divisible by slot_minutes")
    return horizon_minutes // slot_minutes
