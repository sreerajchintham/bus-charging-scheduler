from bus_charging_scheduler.output import solve_and_build_schedule
from bus_charging_scheduler.ui.scenarios import list_scenario_files, scenarios_directory
from bus_charging_scheduler.ui.views import (
    bus_timetable_rows,
    schedule_horizon_minutes,
    station_charging_rows,
    station_utilization_rows,
)
from tests.conftest import MINIMAL_SCENARIO_PATH
from bus_charging_scheduler.scenarios.loader import load_scenario


def test_scenarios_directory_exists():
    assert scenarios_directory().is_dir()


def test_list_scenario_files_includes_minimal():
    names = [path.name for path in list_scenario_files()]
    assert "minimal_valid.yaml" in names


def test_view_helpers_from_schedule(minimal_scenario):
    _, schedule = solve_and_build_schedule(minimal_scenario)
    timetable = schedule.bus_timetables[0]
    rows = bus_timetable_rows(timetable)
    assert len(rows) == 3
    assert rows[0]["station"] == "depot-a"

    order = schedule.station_charging_orders[0]
    util = station_utilization_rows(order, horizon_minutes=60)
    assert util["station"] == "depot-a"
    assert station_charging_rows(order) == []
    assert schedule_horizon_minutes(schedule) >= 0


def test_view_helpers_integration_file():
    scenario = load_scenario(MINIMAL_SCENARIO_PATH)
    _, schedule = solve_and_build_schedule(scenario)
    assert schedule.scenario_name == "example-morning-peak"
