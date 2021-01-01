import matplotlib.pyplot as plt
from line_profile import get_generated_line_info
from plot_settings import get_curve_plot
from cnp_algo import apply_cnp_algo
from tan_algo import apply_tan_algo, get_global_min_delay
import numpy as np


berth_num = 2
line_num = 10
total_flow = 135
arrival_type = "Gaussian"
mean_service = 25
cycle_length = 120
green_ratio = 0.5
buffer_size = 3

# indicator = "flow"
# indicator = "rho"
# queue_rule = "LO-Out"
# queue_rule = "FO-Bus"
# queue_rule = "FIFO"
# set_no = 0

### cnp algorithm setting
sim_budget = 100
max_depth = 5  # must >= 3
sample_num_of_each_region = 3
### figure setting
line_styles_dict = {"FIFO": "solid", "LO-Out": "dashed", "FO-Bus": "dotted"}
line_colors = ["#ff1654", "#0a1128"]


fig, ax = get_curve_plot(
    # x_label="simulaiton rounds", y_label="$\frac{delay}{global minima}$"
    x_label="simulaiton rounds",
    y_label="minimum searched so far / global minimum",
)
### cnp algorithm
for set_no in [0, 1]:
    for queue_rule in ["FIFO", "LO-Out", "FO-Bus"]:
        ### signal setting
        signal_setting = None
        ### stop_setting
        stop_setting = (
            queue_rule,
            berth_num,
            line_num,
            total_flow,
            arrival_type,
            mean_service,
            set_no,
        )
        ### global minimum
        gloabl_min = get_global_min_delay(stop_setting)
        line_color = line_colors[set_no]  # one color for one set_no
        ### cnp algorithm
        algo_setting = (sim_budget, max_depth, sample_num_of_each_region)
        history_delays = apply_cnp_algo(algo_setting, stop_setting, signal_setting)
        norm_history_delays = [x / gloabl_min for x in history_delays]
        x = np.arange(1, len(norm_history_delays) + 1, 1)
        ax.set_xticks(np.arange(1, len(norm_history_delays) + 1, 10))
        ax.plot(
            x,
            norm_history_delays,
            color=line_color,
            linestyle=line_styles_dict[queue_rule],
        )
        line_flow, line_service, line_rho = get_generated_line_info(
            berth_num, line_num, total_flow, arrival_type, mean_service, set_no
        )
        ax.legend([0, 1])


fig_str = "figs_in_paper/c=" + str(berth_num) + "_iso.jpg"
fig.savefig(fig_str)

