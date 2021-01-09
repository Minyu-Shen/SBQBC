from sacred.observers import MongoObserver
from concurrent import futures
from arena import random_assign_plan_enumerator
from line_profile import get_generated_line_info
from experiment import ex
import ast
from isolated_scenario import sim_one_isolated_scenario
from cnp_algo import apply_cnp_algo


@ex.config
def config():
    seed = 1
    queue_rule = "FO-Bus"
    berth_num = 4
    line_num = 16
    total_flow = None
    arrival_type = "Gaussian"
    mean_service = None
    set_no = None
    # is_CNP = True  # True means using CNP, otherwise means perturbation
    is_CNP = False


def run(assign_plan_str):
    if not ex.observers:
        ex.observers.append(MongoObserver(url="localhost:27017", db_name="ttt"))
    run = ex.run(config_updates={"assign_plan_str": assign_plan_str})


(
    queue_rule,
    berth_num,
    line_num,
    total_flow,
    arrival_type,
    mean_service,
    set_no,
    is_CNP,
) = (
    config()["queue_rule"],
    config()["berth_num"],
    config()["line_num"],
    config()["total_flow"],
    config()["arrival_type"],
    config()["mean_service"],
    config()["set_no"],
    config()["is_CNP"],
)
if is_CNP:
    stop_setting = (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    )
    signal_setting = None
    sample_num_of_each_region = 5
    max_depth = 3
    sim_budget = 2
    # ex.info["sim_budget"] = sim_budget
    # ex.info["max_depth"] = max_depth
    # ex.info["sample_num_of_each_region"] = sample_num_of_each_region
    algo_setting = (sim_budget, max_depth, sample_num_of_each_region)
    history_delays = apply_cnp_algo(algo_setting, stop_setting, signal_setting)
    print(history_delays)

else:  # perturbation
    perturb_num = 1000
    enumerator = random_assign_plan_enumerator(line_num, berth_num, perturb_num)
    with futures.ProcessPoolExecutor(max_workers=22) as executor:
        tasks = [executor.submit(run, str(assign_plan)) for assign_plan in enumerator]
        for future in futures.as_completed(tasks):
            pass

