from sacred import Experiment
import numpy as np
from isolated_scenario import sim_one_isolated_scenario
from line_profile import get_generated_line_info
import ast

ex = Experiment()


@ex.automain
def main(_run, berth_num, queue_rule, f, mu_S, line_num, set_no, assign_plan_str):
    print("------------------------ start main ----------------------------")
    flows, services = get_generated_line_info(berth_num, line_num, set_no)
    # print(flows, services)
    is_persistent = False
    assign_plan = ast.literal_eval(assign_plan_str)
    print(assign_plan)
    args = (berth_num, queue_rule, flows, services, is_persistent, assign_plan)
    delay_seq = sim_one_isolated_scenario(*args)
    ex.info["delay_seq"] = delay_seq
    print("delay_seq is:", delay_seq)

    # ex.info['test'] = 'testing'
