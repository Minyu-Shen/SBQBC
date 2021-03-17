from sacred.observers import MongoObserver
from sacred import Experiment
from concurrent import futures
from arena import random_assign_plan_enumerator
from line_profile import get_generated_line_info
from isolated_scenario import sim_one_isolated_scenario
from cnp_algo import apply_cnp_algo

cnp_ex = Experiment()

if not cnp_ex.observers:
    cnp_ex.observers.append(MongoObserver(url="localhost:27017", db_name="ggg"))


@cnp_ex.config
def config():
    seed = 1
    is_CNP = True  # True means using CNP, otherwise means perturbation

    queue_rule = "FO-Bus"
    berth_num = 2
    line_num = 10
    total_flow = 135
    arrival_type = "Gaussian"
    mean_service = 25
    set_no = 0
    stop_setting = (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    )

    # signal
    signal_setting = None

    # algorithm
    sample_num_of_each_region = 5
    max_depth = 4
    sim_budget = 100
    algo_setting = (sim_budget, max_depth, sample_num_of_each_region)


@cnp_ex.automain
def main(algo_setting, stop_setting, signal_setting):
    history_min_delays = apply_cnp_algo(algo_setting, stop_setting, signal_setting)
    cnp_ex.info["history_min_delays"] = history_min_delays
    print(history_min_delays)
