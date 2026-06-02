"""Load and validate scenario YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from bus_charging_scheduler.domain.models import Scenario
from bus_charging_scheduler.scenarios.errors import ScenarioValidationError
from bus_charging_scheduler.scenarios.validation import validate_scenario


def _format_pydantic_errors(exc: ValidationError) -> list[str]:
    return [
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in exc.errors()
    ]


def load_scenario_from_dict(data: dict[str, Any]) -> Scenario:
    """Parse a scenario mapping and run semantic validation."""
    try:
        scenario = Scenario.model_validate(data)
    except ValidationError as exc:
        raise ScenarioValidationError(_format_pydantic_errors(exc)) from exc

    messages = validate_scenario(scenario)
    if messages:
        raise ScenarioValidationError(messages)

    return scenario


def load_scenario(path: Path | str) -> Scenario:
    """Load a scenario YAML file from disk."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"scenario file not found: {file_path}")

    with file_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ScenarioValidationError(
            [f"scenario root must be a mapping, got {type(raw).__name__}"]
        )

    return load_scenario_from_dict(raw)
