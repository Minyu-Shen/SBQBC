from sacred.observers import MongoObserver
from sacred import Experiment
from line_profile import get_generated_line_info
from sim_results import get_delay_of_continuous

simple_ex = Experiment()

if not simple_ex.observers:
    simple_ex.observers.append(MongoObserver(url="localhost:27017", db_name="perturb_stop"))


@simple_ex.config
def config():
    seed = 1
    # stop
    queue_rule = "FO-Bus"
    # queue_rule = "LO-Out"
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
    signal_setting = {
        "cycle_length": cycle_length,
        "green_ratio": green_ratio,
        "buffer_size": buffer_size,
    }


@simple_ex.automain
def main(stop_setting, signal_setting):
    (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    ) = stop_setting

    line_flow, line_service, line_rho = get_generated_line_info(
        berth_num, line_num, total_flow, arrival_type, mean_service, set_no
    )
    sim_info = {
        "queue_rule": queue_rule,
        "berth_num": berth_num,
        "line_flow": line_flow,
        "line_service": line_service,
        "signal": signal_setting,
    }
    total_rho = sum(line_rho.values())
    evenest_point = [total_rho / berth_num] * berth_num

    assign_plan, delay = get_delay_of_continuous(
        line_flow, line_service, evenest_point, run_df=None, sim_info=sim_info
    )
    simple_ex.info["simple_policy_delay"] = delay
