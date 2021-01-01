from numpy import random
from arena import (
    cal_berth_f_rho_for_each_plan,
    get_delay_of_continuous,
    get_run_df_from_db,
    get_run_df_from_near_stop_db,
)
from line_profile import get_generated_line_info
from region import build_region_tree


class Opt_Stats(object):
    def __init__(self, sim_budget):
        self.sim_budget = sim_budget
        self.evaled_assign_plans = []
        self.eval_count = 0

        self.min_delay_so_far = 1.0e4
        self.history_min_delays = []

    def add_eval_info(self, assign_plan, delay):
        if assign_plan not in self.evaled_assign_plans:
            self.eval_count += 1
            self.evaled_assign_plans.append(assign_plan)
            self.min_delay_so_far = min(self.min_delay_so_far, delay)
            self.history_min_delays.append(self.min_delay_so_far)
        else:
            pass

    def is_budget_run_out(self):
        return False if self.eval_count < self.sim_budget else True


def get_global_min_delay(stop_setting, signal_setting=None):
    if signal_setting is None:
        run_df = get_run_df_from_db(stop_setting)
    else:
        run_df = get_run_df_from_near_stop_db(stop_setting, signal_setting)
    run_df["final_delay"] = run_df.delay_seq.apply(lambda x: x[-1])
    return run_df["final_delay"].min().item()


def apply_tan_algo(algo_setting, stop_setting, signal_setting=None):
    ### isolated stop setting
    (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    ) = stop_setting
    ### algorithm hyper-parameters
    radius, region_num = algo_setting

    ### get profile and simulated data
    line_flow, line_service, line_rho = get_generated_line_info(
        berth_num, line_num, total_flow, arrival_type, mean_service, set_no
    )
    if signal_setting is None:
        run_df = get_run_df_from_db(stop_setting)
    else:
        run_df = get_run_df_from_near_stop_db(stop_setting, signal_setting)

    ### find start point and its located region of maximum depth
    evenest_point = [total_rho / berth_num] * berth_num
    assign_plan, delay = get_delay_of_continuous(
        line_flow, line_service, evenest_point, run_df
    )
    berth_flow, berth_rho = cal_berth_f_rho_for_each_plan(
        assign_plan, line_flow, line_service
    )
    print("--------- end iteration -----------")
    # print(opt_stats.min_delay_so_far, opt_stats.eval_count)

    return None
