from experiment import ex
from sacred.observers import MongoObserver
from concurrent import futures
from line_profile import generate_line_info, get_generated_line_info
from arena import assign_plan_enumerator


@ex.config
def config():
    seed = 1
    # queue_rule = "LO-Out"
    queue_rule = "FIFO"
    berth_num = 2
    line_num = 8
    total_flow = 135  # buses/hr
    arrival_type = "Gaussian"
    mean_service = 25  # seconds
    set_no = 0


def run(assign_plan_str):
    if not ex.observers:
        ex.observers.append(MongoObserver(url="localhost:27017", db_name="stop"))
    run = ex.run(config_updates={"assign_plan_str": assign_plan_str})


line_num, berth_num = config()["line_num"], config()["berth_num"]
enumerator = assign_plan_enumerator(line_num, berth_num)
assign_plans = [plan for plan in enumerator]
# assign_plans = assign_plans[0:1]
# assign_plans = [None]
with futures.ProcessPoolExecutor(max_workers=18) as executor:
    tasks = [executor.submit(run, str(assign_plan)) for assign_plan in assign_plans]
    for future in futures.as_completed(tasks):
        pass

