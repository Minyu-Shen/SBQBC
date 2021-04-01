from sacred.observers import MongoObserver
from sacred import Experiment
from cnp_algo import apply_cnp_algo

### for c=4 case, directly simulate, (without accessing the cache)
cnp_ex = Experiment()

if not cnp_ex.observers:
    cnp_ex.observers.append(MongoObserver(url="localhost:27017", db_name="c4_case"))
    # cnp_ex.observers.append(MongoObserver(url="localhost:27017", db_name="ggg"))


@cnp_ex.config
def config():
    seed = 6
    is_CNP = True  # True means using CNP, otherwise means perturbation

    queue_rule = "FIFO"
    # queue_rule = "FO-Free"
    berth_num = 4
    line_num = 12
    total_flow = None
    arrival_type = "Gaussian"
    mean_service = None
    set_no = None
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
    cycle_length = 120
    green_ratio = 0.5
    buffer_size = 3
    signal_setting = (cycle_length, green_ratio, buffer_size)

    # algorithm
    sample_num_of_each_region = 10
    max_depth = 4
    sim_budget = 500
    algo_setting = (sim_budget, max_depth, sample_num_of_each_region)


@cnp_ex.automain
def main(algo_setting, stop_setting, signal_setting):
    history_min_delays = apply_cnp_algo(algo_setting, stop_setting, signal_setting)
    cnp_ex.info["history_min_delays"] = history_min_delays
    print(history_min_delays)
