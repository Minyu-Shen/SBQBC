import matplotlib.pyplot as plt
from arena import (
    cal_berth_f_rho_for_each_plan,
    plot_contour_by_lists,
    get_run_df_from_db,
    get_run_df_from_near_stop_db,
)
from line_profile import get_generated_line_info
import numpy as np
from hyper_parameters import max_tolerance_delay


berth_num = 2
line_num = 6
total_flow = 135
arrival_type = "Gaussian"
# queue_rule = "LO-Out"
queue_rule = "FIFO"
mean_service = 25
set_no = 0
cycle_length = 140
green_ratio = 0.5
buffer_size = 4

indicator = "flow"
indicator = "rho"

# run_df = get_run_df_from_db(
#     queue_rule, berth_num, line_num, total_flow, arrival_type, mean_service, set_no
# )
run_df = get_run_df_from_near_stop_db(
    queue_rule,
    berth_num,
    line_num,
    total_flow,
    arrival_type,
    mean_service,
    set_no,
    cycle_length,
    green_ratio,
    buffer_size,
)

line_flow, line_service, line_rho = get_generated_line_info(
    berth_num, line_num, total_flow, arrival_type, mean_service, set_no
)
# max_tolerance_delay = 1.0e8
x, y, z = [], [], []
min_delay = 1.0e5
for _, row in run_df.iterrows():
    berth_flow, berth_rho = cal_berth_f_rho_for_each_plan(
        row["assign_plan_str"], line_flow, line_service
    )
    delay = row["delay_seq"][-1]
    # if delay < max_tolerance_delay:
    if delay < 300.0:
        if indicator == "rho":
            x.append(berth_rho[0])
            y.append(berth_rho[1])
        else:
            x.append(berth_flow[0])
            y.append(berth_flow[1])
        z.append(delay)
    min_delay = min(min_delay, delay)
print("min delay is: ", min_delay)

if berth_num == 2:
    fig, ax = plt.subplots()
    if indicator == "rho":
        ax.set_xlabel("rho_0 - rho_1")
        # ax.set_xlim(-0.03, 0.03)
    else:
        ax.set_xlabel("flow_0 - flow_1")
    ax.set_ylabel("delay (seconds)")
    diffs = [xi - yi for xi, yi in zip(x, y)]
    ax.scatter(diffs, z)
    fig_str = (
        "figs/2_berth_"
        + str(line_num)
        + "_line_"
        + queue_rule
        + "_"
        + indicator
        + "_general_view.jpg"
    )
    fig.savefig(fig_str)
else:
    fig = plot_contour_by_lists(x, y, z)
    fig_str = "figs/3_berth_" + queue_rule + "_general_view.jpg"
    fig.savefig(fig_str)

