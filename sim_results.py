from miqp import get_closest_discrete_from_continuous
from isolated_scenario import sim_one_isolated_scenario
from signal_scenario import sim_one_NS_scenario


def get_delay_of_continuous(
    line_flow, line_service, continuous_vector, run_df=None, sim_info=None
):
    # find the closest discrete assignment plan
    assign_plan = get_closest_discrete_from_continuous(
        line_flow, line_service, continuous_vector
    )
    delay = get_delay_of_discrete_plan(assign_plan, run_df, sim_info)
    return assign_plan, delay


def get_delay_of_discrete_plan(assign_plan, run_df, sim_info=None):
    if run_df is None or run_df.empty:  # no cache, directly simulate
        if sim_info["signal"] == None:
            delay = sim_one_isolated_scenario(
                sim_info["queue_rule"],
                sim_info["berth_num"],
                sim_info["line_flow"],
                sim_info["line_service"],
                False,
                assign_plan,
            )
            return delay
    else:
        assign_plan_str = str(assign_plan)
        query_str = "assign_plan_str==@assign_plan_str"
        df = run_df.query(query_str)
        if df.empty:
            return None
        else:
            df = df.iloc[0, :]
            delay = df["delay_seq"][-1]
            return delay
