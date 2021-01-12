from sacred.observers import MongoObserver
from concurrent import futures
from arena import random_assign_plan_enumerator
from signal_experiment import signal_ex


@signal_ex.config
def config():
    seed = 1
    queue_rule = "FO-Bus"
    # queue_rule = "LO-Out"
    berth_num = 4
    line_num = 12
    total_flow = None
    arrival_type = "Gaussian"
    mean_service = None
    set_no = None
    is_CNP = False  # True means using CNP, otherwise means perturbation
    cycle_length = 120
    green_ratio = 0.5
    buffer_size = 3


def run(assign_plan_str):
    if not signal_ex.observers:
        signal_ex.observers.append(
            MongoObserver(url="localhost:27017", db_name="perturb_stop")
        )
    run = signal_ex.run(config_updates={"assign_plan_str": assign_plan_str})


perturb_num = 500
berth_num, line_num = config()["berth_num"], config()["line_num"]
enumerator = random_assign_plan_enumerator(line_num, berth_num, perturb_num)
with futures.ProcessPoolExecutor(max_workers=22) as executor:
    tasks = [executor.submit(run, str(assign_plan)) for assign_plan in enumerator]
    for future in futures.as_completed(tasks):
        pass
