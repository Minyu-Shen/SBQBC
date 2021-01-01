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
    berth_num, line_num, total_flow, arrival_type, mean_service, set_no, queue_rule,
):
    print("------------------------ start main ----------------------------")
    for sim_budget in [100]:
        for max_depth in [4]:
            for sample_num_of_each_region in [3]:
                algo_ex.info["sim_budget"] = sim_budget
                algo_ex.info["max_depth"] = max_depth
                algo_ex.info["sample_num_of_each_region"] = sample_num_of_each_region
                ### signal setting
                signal_setting = None
                algo_ex.info["signal_setting"] = signal_setting
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
                ### global minimum
                gloabl_min = get_global_min_delay(stop_setting)
                ### cnp algorithm
                algo_setting = (sim_budget, max_depth, sample_num_of_each_region)
                history_delays = apply_cnp_algo(
                    algo_setting, stop_setting, signal_setting
                )
                norm_history_delays = [x / gloabl_min for x in history_delays]
                algo_ex.info["norm_history_delays"] = norm_history_delays

    # ex.info['test'] = 'testing'

