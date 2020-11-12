import numpy as np
from isolated_scenario import sim_one_isolated_scenario
from arena import generate_line_info

np.random.seed(0)
berth_num = 2
queue_rule = "FIFO"
f = 170.0  # buses/hr
mu_S = 25  # seconds
line_no = 1

for case in range(1):
    flows, services = generate_line_info(line_no, f, mu_S, service_cvs=(0.5, 0.5))
    assign_plan = None
    arg = (berth_num, queue_rule, flows, services, False, assign_plan)
    delay = sim_one_isolated_scenario(arg)

    # results = []
    # all_plans = make_assign_plan(line_no, berth_num, flows, services)
    # with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
    #     args = (
    #         (berth_num, queue_rule, flows, services, False, assign_plan)
    #         for assign_plan in all_plans
    #     )
    #     for result in executor.map(sim_one_isolated_scenario, args):
    #         # plan, delay = result
    #         results.append(result)

    # with open("test.pkl", "wb") as f:
    #     pickle.dump([results, flows, services], f)

# with open('one.pkl', 'rb') as f:
#     results, flows, services = pickle.load(f)
#     plot_dict = {}
#     for result in results:
#         plan, delay = result
#         rho_plan_dict = calculate_rho(plan, flows, services)
#         rho_ratio = abs(rho_plan_dict[0] - rho_plan_dict[1])
#         # print(plan, rho_ratio, delay)
#         if delay <= 300: plot_dict[rho_ratio] = delay

#     lists = sorted(plot_dict.items()) # sorted by key, return a list of tuples
#     x, y = zip(*lists) # unpack a list of pairs into two tuples
#     plt.plot(x, y)
#     plt.show()