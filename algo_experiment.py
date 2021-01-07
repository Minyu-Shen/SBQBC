from sacred import Experiment
from signal_scenario import sim_one_NS_scenario
from line_profile import get_generated_line_info
from cnp_algo import apply_cnp_algo
from tan_algo import apply_tan_algo, get_global_min_delay
from sacred.observers import MongoObserver

algo_ex = Experiment()
algo_ex.observers.append(MongoObserver(url="localhost:27017", db_name="numerical_case"))


@algo_ex.automain
def main(
    algorithm,
    berth_num,
    line_num,
    total_flow,
    arrival_type,
    mean_service,
    set_no,
    queue_rule,
    cycle_length,
    green_ratio,
    buffer_size,
):
    print("------------------------ start main ----------------------------")
    ### stop_setting
    stop_setting = (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    )
    ### signal setting
    if cycle_length is not None:
        signal_setting = (cycle_length, green_ratio, buffer_size)
    else:
        signal_setting = None

    ### global minimum
    gloabl_min = get_global_min_delay(stop_setting, signal_setting)

    if algorithm == "Tan":
        for radius in [0.05 * 1.5]:  # 0.05 * 1.5
            # for radius in [0.05]:
            for region_num in [16]:  # 16
                # for region_num in [24]:
                algo_setting = (radius, region_num)
                history_delays = apply_tan_algo(
                    algo_setting, stop_setting, signal_setting
                )
                norm_history_delays = [x / gloabl_min for x in history_delays]
                algo_ex.info["norm_history_delays"] = norm_history_delays
    else:
        for sim_budget in [200]:
            for max_depth in [5]:
                for sample_num_of_each_region in [5]:
                    algo_ex.info["sim_budget"] = sim_budget
                    algo_ex.info["max_depth"] = max_depth
                    algo_ex.info[
                        "sample_num_of_each_region"
                    ] = sample_num_of_each_region
                    ### cnp algorithm
                    algo_setting = (sim_budget, max_depth, sample_num_of_each_region)
                    history_delays = apply_cnp_algo(
                        algo_setting, stop_setting, signal_setting
                    )
                    norm_history_delays = [x / gloabl_min for x in history_delays]
                    algo_ex.info["norm_history_delays"] = norm_history_delays

        # ex.info['test'] = 'testing'

