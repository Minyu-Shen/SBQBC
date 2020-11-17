from numpy import random
from arena import (
    cal_berth_rho_for_each_plan,
    get_delay_of_continuous,
    get_run_df_from_db,
)
from line_profile import get_generated_line_info
from region import build_region_tree
from operator import attrgetter
from collections import defaultdict


class Opt_Stats(object):
    def __init__(self, curr_promising_region_id, curr_depth, sim_budget):
        self.sim_budget = sim_budget
        self.evaled_assign_plans = []
        self.eval_count = 0

        self.curr_depth = curr_depth
        self.min_delay_so_far = 1.0e4
        self.curr_promising_region_id = curr_promising_region_id

    def add_eval_info(self, assign_plan, delay):
        if assign_plan not in self.evaled_assign_plans:
            self.eval_count += 1
            self.evaled_assign_plans.append(assign_plan)
            self.min_delay_so_far = min(self.min_delay_so_far, delay)
        else:
            pass

    def is_budget_run_out(self):
        return False if self.eval_count < self.sim_budget else True


berth_num = 3
line_num = 6
total_flow = 160
arrival_type = "Gaussian"
mean_service = 25
set_no = 0

### algorithm hyper-parameters
sim_budget = 100
max_depth = 4  # must >= 3
sample_num_of_each_region = 2

### build tree
total_region_list = build_region_tree(dim=berth_num, max_depth=max_depth)
root_region = total_region_list[0]
root_region.print_tree()

### get profile and simulated data
run_df = get_run_df_from_db(
    berth_num, line_num, total_flow, arrival_type, mean_service, set_no
)
line_flow, line_service, line_rho = get_generated_line_info(
    berth_num, line_num, total_flow, arrival_type, mean_service, set_no
)

### find start point and its located region of maximum depth
curr_promising_region_id = -1
curr_depth = -1
regions_at_max_depth = [
    region for region in total_region_list if region.depth == max_depth - 1
]
total_rho = sum(line_rho.values())
evenest_point = [total_rho / berth_num] * berth_num
assign_plan, delay = get_delay_of_continuous(
    line_flow, line_service, evenest_point, run_df
)
berth_rho = cal_berth_rho_for_each_plan(assign_plan, line_flow, line_service)
for region in regions_at_max_depth:
    unit_berth_rho = [x / total_rho for x in berth_rho]
    is_contain = region.is_point_in_region(unit_berth_rho)
    if is_contain:
        curr_promising_region_id = region.region_id
        curr_depth = region.depth

opt_stats = Opt_Stats(curr_promising_region_id, curr_depth, sim_budget)
opt_stats.add_eval_info(assign_plan, delay)
print("--------- start region is: ", opt_stats.curr_promising_region_id, "-----------")

### start iteration
print(opt_stats.min_delay_so_far, opt_stats.eval_count)
print("--------- start iteration -----------")
while True:
    if opt_stats.is_budget_run_out():
        break
    curr_promising_region = total_region_list[opt_stats.curr_promising_region_id]
    if curr_promising_region.depth == 0:  # at root node
        print("--------- at root -----------")
        best_child_region_tuple = curr_promising_region.evaluate_children_return_best(
            sample_num_of_each_region, line_flow, line_service, opt_stats, run_df
        )
        best_child_region_id, best_delay_list = best_child_region_tuple
        opt_stats.curr_promising_region_id = best_child_region_id
    else:
        # evaluate "combined" big surrounding region
        surrounding_sample_delays = []
        surrounding_region_list = [
            region
            for region in total_region_list
            if region.depth == curr_promising_region.depth
            and region.region_id != curr_promising_region.region_id
        ]
        for _ in range(sample_num_of_each_region):
            # uniformly select one surrounding region
            sampled_region = random.choice(surrounding_region_list)
            assign_plan, delay = sampled_region.sample_one_plan(
                line_flow, line_service, run_df
            )
            opt_stats.add_eval_info(assign_plan, delay)
            surrounding_sample_delays.append(delay)

        if curr_promising_region.depth == max_depth - 1:  # at leaf node
            print("--------- at max depth -----------")
            promising_sample_delays = []
            # further explore promising region
            for _ in range(sample_num_of_each_region):
                assign_plan, delay = curr_promising_region.sample_one_plan(
                    line_flow, line_service, run_df
                )
                opt_stats.add_eval_info(assign_plan, delay)
                promising_sample_delays.append(delay)

            # compare indexs and see if trackback or not
            if min(surrounding_sample_delays) < min(promising_sample_delays):
                opt_stats.curr_promising_region_id = (
                    curr_promising_region.parent.region_id
                )
            print(opt_stats.curr_promising_region_id)

        else:  # 0 < curr_depth < max_depth-1
            print("---------at intermedium depth-----------")
            best_child_region_tuple = curr_promising_region.evaluate_children_return_best(
                sample_num_of_each_region, line_flow, line_service, opt_stats, run_df
            )
            best_child_region_id, best_delay_list = best_child_region_tuple
            # print(child_region_sample_delays_dict)
            # print(best_child_region_id, best_delay_list)
            if min(surrounding_sample_delays) < min(best_delay_list):
                opt_stats.curr_promising_region_id = (
                    curr_promising_region.parent.region_id
                )
            else:
                opt_stats.curr_promising_region_id = best_child_region_id

print(opt_stats.min_delay_so_far, opt_stats.eval_count)
