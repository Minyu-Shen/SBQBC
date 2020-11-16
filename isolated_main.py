from experiment import ex
from sacred.observers import MongoObserver
from concurrent import futures
from line_profile import generate_line_info, get_generated_line_info
from arena import assign_plan_enumerator


@ex.config
def config():
    seed = 1
    queue_rule = "FIFO"
    berth_num = 3
    line_num = 6
    total_flow = 160  # buses/hr
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


# line_profile = get_generated_line_info(berth_num=2, line_num=6, set_no=0)
# print(line_profile)

# ex.observers.append(MongoObserver(url="localhost:27017", db_name="stop"))
# ex.run(config_updates={"assign_plan": })


# mu_Ss = [x for x in range(5, 26, 1)]
# with futures.ProcessPoolExecutor(max_workers=10) as executor:
#     tasks = [executor.submit(run, mu_S) for mu_S in mu_Ss]
#     for future in futures.as_completed(tasks):
#         print("finished ... ")

