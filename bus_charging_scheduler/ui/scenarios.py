"""Scenario discovery for the UI (no Streamlit dependency)."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def scenarios_directory() -> Path:
    return project_root() / "data" / "scenarios"


def list_scenario_files() -> list[Path]:
    directory = scenarios_directory()
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.yaml"))
