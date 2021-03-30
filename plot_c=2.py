import matplotlib.pyplot as plt
from line_profile import get_generated_line_info
from plot_settings import get_curve_plot
import numpy as np
from arena import get_case_df_from_db


berth_num = 2
line_num = 10
total_flow = 135
arrival_type = "Gaussian"
mean_service = 25
signal_setting = None
# signal_setting = (120, 0.5, 3)

### figure setting
# line_styles_dict = {"FIFO": "solid", "LO-Out": "dashed", "FO-Free": "dotted"}

# algo_line_colors_dict = {"Tan": "#ff1654", "CNP": "#0a1128"}
algo_line_colors_dict = {"Tan": "black", "CNP": "red"}
setno_styles_dict = {0: "solid", 1: "dashed", 2: "dotted"}
setno_styles_dict = {0: "solid", 1: "dotted", 2: "dashed"}

if signal_setting is None:
    ann_text_pos = {"FIFO": (60, 1.07), "LO-Out": (50, 1.20), "FO-Free": (60, 1.13)}
else:
    ann_text_pos = {"FIFO": (60, 1.03), "LO-Out": (60, 1.25), "FO-Free": (70, 1.08)}

for queue_rule in ["FIFO", "LO-Out", "FO-Free"]:
    ### generate figures for each queueing rule
    fig, ax = get_curve_plot(
        # x_label="simulaiton rounds", y_label="$\frac{delay}{global minima}$"
        x_label="Simulaiton rounds",
        y_label="Searched minimum / global minimum",
        x_font=14,
        y_font=14,
    )

    y_max_lim = 0.0
    set_str_count = 1
    for set_no in [0, 1]:
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
        print("----", queue_rule, "----")
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
        ax.set_xticks(x_ticks)
        ax.set_xlim([-1, 100])
        ax.tick_params(axis="both", which="major", labelsize=13)

        tan_label = "Tan et al. (2014), line set-" + str(set_str_count)
        ax.plot(
            x_tan,
            tan_norm_history_delays,
            color=algo_line_colors_dict["Tan"],
            linestyle=setno_styles_dict[set_no],
            linewidth=1.5,
            label=tan_label,
        )
        cnp_label = "Proposed CNP, line set-" + str(set_str_count)
        ax.plot(
            x_cnp,
            cnp_norm_history_delays,
            color=algo_line_colors_dict["CNP"],
            linestyle=setno_styles_dict[set_no],
            linewidth=1.5,
            label=cnp_label,
        )
        line_flow, line_service, line_rho = get_generated_line_info(
            berth_num, line_num, total_flow, arrival_type, mean_service, set_no
        )
        # annotating simple policy
        ax.annotate(
            "simple policy",
            xy=(1, cnp_norm_history_delays[0]),
            xytext=ann_text_pos[queue_rule],
            size=14,
            va="center",
            ha="center",
            bbox=dict(boxstyle="round4", fc="w"),
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3,rad=0.0",
                relpos=(0.5, 0.0),
                fc="w",
            ),
        )
        ax.plot(
            x_cnp[0], cnp_norm_history_delays[0], "rD",
        )
        ax.legend(fontsize=14)
        y_max_lim = max(cnp_norm_history_delays[0], y_max_lim)
        set_str_count += 1

    ax.set_ylim([0.98, y_max_lim + 0.1])

    if signal_setting is not None:
        fig_str = "figs_in_paper/c=" + str(berth_num) + "_" + queue_rule + "_signal.jpg"
    else:
        fig_str = "figs_in_paper/c=" + str(berth_num) + "_" + queue_rule + "_iso.jpg"
    fig.savefig(fig_str)

