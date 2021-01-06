from signal_experiment import signal_ex
from sacred.observers import MongoObserver
from concurrent import futures
from line_profile import generate_line_info, get_generated_line_info
from arena import assign_plan_enumerator


@signal_ex.config
def config():
    seed = 1
    # queue_rule = "FIFO"
    # queue_rule = "LO-Out"
    queue_rule = "FO-Bus"
    berth_num = 2
    line_num = 12
    total_flow = 138  # buses/hr
    arrival_type = "Gaussian"
    mean_service = 25  # seconds
    cycle_length = 120
    green_ratio = 0.5
    buffer_size = 3
    set_no = 0  # which set of input profile in the database


def run(assign_plan_str):
    if not signal_ex.observers:
        signal_ex.observers.append(
            MongoObserver(url="localhost:27017", db_name="near_stop")
        )
    run = signal_ex.run(config_updates={"assign_plan_str": assign_plan_str})


line_num, berth_num = config()["line_num"], config()["berth_num"]
enumerator = assign_plan_enumerator(line_num, berth_num)
assign_plans = [plan for plan in enumerator]
# assign_plans = assign_plans[0:1]
# assign_plans = [None]
with futures.ProcessPoolExecutor(max_workers=22) as executor:
    tasks = [executor.submit(run, str(assign_plan)) for assign_plan in assign_plans]
    for future in futures.as_completed(tasks):
        pass
