"""Streamlit UI for bus charging scheduling."""

from __future__ import annotations

import streamlit as st

from bus_charging_scheduler.output.pipeline import solve_and_build_schedule
from bus_charging_scheduler.scenarios.errors import ScenarioValidationError
from bus_charging_scheduler.scenarios.loader import load_scenario
from bus_charging_scheduler.solver.errors import SolverError
from bus_charging_scheduler.ui.scenarios import list_scenario_files
from bus_charging_scheduler.ui.views import (
    bus_timetable_rows,
    schedule_horizon_minutes,
    station_charging_rows,
    station_utilization_rows,
)


def main() -> None:
    st.set_page_config(page_title="Bus Charging Scheduler", layout="wide")
    st.title("Bus Charging Scheduler")
    st.caption("Scenario-driven CP-SAT scheduling for electric bus fleets")

    scenario_paths = list_scenario_files()
    if not scenario_paths:
        st.error("No scenario YAML files found in data/scenarios/")
        return

    labels = [path.stem for path in scenario_paths]
    selected_label = st.sidebar.selectbox("Scenario", labels)
    selected_path = scenario_paths[labels.index(selected_label)]

    st.sidebar.markdown(f"**File:** `{selected_path.name}`")

    yaml_text = selected_path.read_text(encoding="utf-8")
    with st.expander("Scenario input (YAML)", expanded=True):
        st.code(yaml_text, language="yaml")

    run_clicked = st.sidebar.button("Run scheduler", type="primary")

    if run_clicked:
        _run_scheduler(selected_path)

    schedule = st.session_state.get("schedule")
    if schedule is None:
        st.info("Select a scenario and click **Run scheduler** to build a timetable.")
        return

    st.subheader("Schedule summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", schedule.status_name)
    col2.metric("Time slot (min)", schedule.slot_minutes)
    col3.metric("Buses scheduled", len(schedule.bus_timetables))

    st.subheader("Bus timetables")
    for timetable in schedule.bus_timetables:
        st.markdown(f"**{timetable.bus_id}** — operator `{timetable.operator_id}`, route `{timetable.route_id}`")
        st.dataframe(bus_timetable_rows(timetable), use_container_width=True)

    horizon = schedule_horizon_minutes(schedule)
    st.subheader("Station utilization")
    utilization = [
        station_utilization_rows(order, horizon_minutes=max(horizon, 1))
        for order in schedule.station_charging_orders
    ]
    st.dataframe(utilization, use_container_width=True)

    st.subheader("Station charging order")
    for order in schedule.station_charging_orders:
        st.markdown(f"**{order.station_id}** ({order.charger_count} charger(s))")
        rows = station_charging_rows(order)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.write("No charging sessions at this station.")


def _run_scheduler(path) -> None:
    try:
        scenario = load_scenario(path)
    except ScenarioValidationError as exc:
        st.session_state.pop("schedule", None)
        st.error("Scenario validation failed:\n" + "\n".join(f"- {msg}" for msg in exc.messages))
        return

    with st.spinner("Solving with OR-Tools CP-SAT..."):
        try:
            _, schedule = solve_and_build_schedule(scenario)
        except SolverError as exc:
            st.session_state.pop("schedule", None)
            st.error(str(exc))
            return

    st.session_state["schedule"] = schedule
    st.success(f"Schedule ready for **{schedule.scenario_name}** ({schedule.status_name}).")


if __name__ == "__main__":
    main()
