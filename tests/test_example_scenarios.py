import pytest

from bus_charging_scheduler.output import solve_and_build_schedule
from bus_charging_scheduler.scenarios.loader import load_scenario
from bus_charging_scheduler.ui.scenarios import list_scenario_files


@pytest.mark.parametrize("scenario_path", list_scenario_files(), ids=lambda p: p.stem)
def test_example_scenario_loads_and_solves(scenario_path):
    scenario = load_scenario(scenario_path)
    _, schedule = solve_and_build_schedule(scenario)
    assert schedule.status_name in {"OPTIMAL", "FEASIBLE"}
    assert len(schedule.bus_timetables) == len(scenario.buses)
