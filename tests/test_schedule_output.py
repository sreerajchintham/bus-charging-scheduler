from bus_charging_scheduler.output import build_schedule, solve_and_build_schedule
from bus_charging_scheduler.scenarios.loader import load_scenario
from bus_charging_scheduler.solver import solve_scenario
from tests.conftest import MINIMAL_SCENARIO_PATH


def test_build_schedule_bus_timetable(minimal_scenario):
    result = solve_scenario(minimal_scenario)
    schedule = build_schedule(minimal_scenario, result)

    assert schedule.scenario_name == "test-scenario"
    assert len(schedule.bus_timetables) == 1

    timetable = schedule.bus_timetables[0]
    assert timetable.bus_id == "bus-01"
    assert len(timetable.visits) == 3
    assert timetable.visits[0].station_id == "depot-a"
    assert timetable.visits[0].arrival_minutes == 0
    assert timetable.visits[0].leg_to_station_id == "terminal-b"
    assert timetable.visits[-1].station_id == "depot-a"
    assert timetable.visits[-1].departure_minutes == timetable.visits[-1].arrival_minutes


def test_station_charging_order_sorted_by_start(minimal_scenario):
    result = solve_scenario(minimal_scenario)
    schedule = build_schedule(minimal_scenario, result)

    for order in schedule.station_charging_orders:
        starts = [session.start_minutes for session in order.sessions]
        assert starts == sorted(starts)


def test_solve_and_build_schedule_integration():
    scenario = load_scenario(MINIMAL_SCENARIO_PATH)
    result, schedule = solve_and_build_schedule(scenario)

    assert result.status_name in {"OPTIMAL", "FEASIBLE"}
    assert schedule.status_name == result.status_name
    assert schedule.bus_timetables[0].route_id == "run-101"
