import matplotlib.pyplot as plt
from line_profile import get_generated_line_info
from plot_settings import get_curve_plot
from cnp_algo import apply_cnp_algo
from tan_algo import apply_tan_algo, get_global_min_delay
import numpy as np
from arena import get_case_df_from_db


berth_num = 2
line_num = 10
total_flow = 135
arrival_type = "Gaussian"
mean_service = 25
cycle_length = 120
green_ratio = 0.5
buffer_size = 3

### cnp algorithm setting
sim_budget = 100
max_depth = 5  # must >= 3
sample_num_of_each_region = 3
### figure setting
line_styles_dict = {"FIFO": "solid", "LO-Out": "dashed", "FO-Bus": "dotted"}
line_colors = ["#ff1654", "#0a1128"]

algo_line_colors_dict = {"Tan": "#ff1654", "CNP": "#0a1128"}
setno_styles_dict = {0: "solid", 1: "dashed", 2: "dotted"}


### cnp algorithm
# for queue_rule in ["FIFO"]:
for queue_rule in ["FIFO", "LO-Out", "FO-Bus"]:
    ### generate figures for each queueing rule
    fig, ax = get_curve_plot(
        # x_label="simulaiton rounds", y_label="$\frac{delay}{global minima}$"
        x_label="simulaiton rounds",
        y_label="searched minimum/ global minimum",
    )
    ### signal setting
    # signal_setting = None
    signal_setting = (120, 0.5, 3)

    for set_no in [1]:
        # line_color = line_colors[set_no]  # one color for one set_no
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
        ### result df
        tan_case_df = get_case_df_from_db(stop_setting, signal_setting, algorithm="Tan")
        tan_norm_history_delays = tan_case_df.norm_history_delays.tolist()[0]
        cnp_case_df = get_case_df_from_db(stop_setting, signal_setting, algorithm="CNP")
        cnp_norm_history_delays = cnp_case_df.norm_history_delays.tolist()[0]

        ### set range
        x_range = max(len(cnp_norm_history_delays), len(tan_norm_history_delays)) + 1
        x_cnp = np.arange(1, len(cnp_norm_history_delays) + 1, 1)
        x_tan = np.arange(1, len(tan_norm_history_delays) + 1, 1)
        x_ticks = [1]
        x_ticks.extend(list(np.arange(10, x_range, 10)))

        ### plot
        ax.set_xticks(x_ticks)
        ax.set_ylim([1, 1.5])
        ax.set_xlim([1, x_range])
        ax.plot(
            x_tan,
            tan_norm_history_delays,
            color=algo_line_colors_dict["Tan"],
            linestyle=setno_styles_dict[set_no],
        )
        ax.plot(
            x_cnp,
            cnp_norm_history_delays,
            color=algo_line_colors_dict["CNP"],
            linestyle=setno_styles_dict[set_no],
        )
        line_flow, line_service, line_rho = get_generated_line_info(
            berth_num, line_num, total_flow, arrival_type, mean_service, set_no
        )

    if signal_setting is not None:
        fig_str = "figs_in_paper/c=" + str(berth_num) + "_" + queue_rule + "_signal.jpg"
    else:
        fig_str = "figs_in_paper/c=" + str(berth_num) + "_" + queue_rule + "_iso.jpg"
    fig.savefig(fig_str)

