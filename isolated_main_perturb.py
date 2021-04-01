from sacred.observers import MongoObserver
from concurrent import futures
from arena import random_assign_plan_enumerator
from experiment import ex


@ex.config
def config():
    seed = 6
    queue_rule = "FIFO"
    # queue_rule = "LO-Out"
    berth_num = 4
    line_num = 12
    total_flow = None
    arrival_type = "Gaussian"
    mean_service = None
    set_no = None
    is_CNP = False  # True means using CNP, otherwise means perturbation

    signal_setting = None


def run(assign_plan_str):
    if not ex.observers:
        ex.observers.append(MongoObserver(url="localhost:27017", db_name="c4_case"))
        # ex.observers.append(
        #     MongoObserver(url="localhost:27017", db_name="perturb_stop")
        # )
    run = ex.run(config_updates={"assign_plan_str": assign_plan_str})


perturb_num = 500
berth_num, line_num = config()["berth_num"], config()["line_num"]
enumerator = random_assign_plan_enumerator(line_num, berth_num, perturb_num)
with futures.ProcessPoolExecutor(max_workers=21) as executor:
    tasks = [executor.submit(run, str(assign_plan)) for assign_plan in enumerator]
    for future in futures.as_completed(tasks):
        pass
