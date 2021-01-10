from sacred.observers import MongoObserver
from sacred import Experiment
from line_profile import get_generated_line_info
from sim_results import get_delay_of_continuous

cnp_ex = Experiment()

if not cnp_ex.observers:
    cnp_ex.observers.append(
        MongoObserver(url="localhost:27017", db_name="perturb_stop")
    )


@cnp_ex.config
def config():
    seed = 1
    # is_CNP = True  # True means using CNP, otherwise means perturbation

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
    signal_setting = None


@cnp_ex.automain
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
        "signal": None,
    }
    total_rho = sum(line_rho.values())
    evenest_point = [total_rho / berth_num] * berth_num

    assign_plan, delay = get_delay_of_continuous(
        line_flow, line_service, evenest_point, run_df=None, sim_info=sim_info
    )
    cnp_ex.info["simple_policy_delay"] = delay
