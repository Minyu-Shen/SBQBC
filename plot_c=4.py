import matplotlib.pyplot as plt
from plot_settings import get_curve_plot
import numpy as np
from arena import sacred_to_df
from pymongo import MongoClient
import pandas as pd

client = MongoClient("localhost", 27017)
db = client["c4_case"]
# collection = db["runs"]

berth_num = 4
line_num = 12
arrival_type = "Gaussian"
queue_rule = "FIFO"
signal_setting = None
signal_setting = (120, 0.5, 3)

db_query = {
    "config.queue_rule": queue_rule,
    "config.berth_num": berth_num,
    "config.line_num": line_num,
    "config.arrival_type": arrival_type,
}

if signal_setting is not None:
    db_query["config.cycle_length"] = signal_setting[0]
else:
    db_query["config.cycle_length"] = None


if signal_setting is None:
    db_query["config.signal_setting"] = None
else:
    db_query["config.cycle_length"] = signal_setting[0]
    db_query["config.green_ratio"] = signal_setting[1]
    db_query["config.buffer_size"] = signal_setting[2]

df = sacred_to_df(db.runs, db_query)
### CNP df
cnp_df = df[df["is_CNP"] == True].copy()
cnp_delays = cnp_df["history_min_delays"].tolist()[0]

### perturb df
perturb_df = df[df["is_CNP"] == False].copy()
perturb_df["delay"] = perturb_df["delay_seq"].apply(
    lambda x: x[-1] if isinstance(x, list) else None
)
perturb_delays = perturb_df["delay"].to_numpy()
sorted_perturb_delays = np.sort(perturb_delays)

# ### generate figures for each queueing rule
fig, ax = get_curve_plot(
    x_label="Number of allocation plans simulated",
    y_label="Average bus delay",
    x_font=15,
    y_font=15,
)

# ### set range
perturb_x = np.arange(1, len(sorted_perturb_delays) + 1, 1)
x_ticks = [1]
x_ticks.extend(list(np.arange(50, len(sorted_perturb_delays) + 1, 50)))

cnp_x = np.arange(1, len(cnp_delays) + 1, 1)

# # ### plot
ax.set_xticks(x_ticks)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.set_xlim([-10, 500])
ax.set_ylim([65, 110])
ax.plot(
    perturb_x,
    sorted_perturb_delays,
    linestyle="dotted",
    color="k",
    label="Uniformly sampling, sorted in ascending order",
)
ax.plot(cnp_x, cnp_delays, linestyle="solid", color="k", label="Proposed CNP method")
ax.legend()

# ax.hlines(sorted_perturb_delays[0], 0, 500, "k", "dashed")

ax.annotate(
    "simple policy",
    xy=(1, cnp_delays[0]),
    xytext=(100, cnp_delays[0] + 20),
    size=14,
    va="center",
    ha="center",
    bbox=dict(boxstyle="round4", fc="w"),
    arrowprops=dict(
        arrowstyle="->", connectionstyle="arc3,rad=0.0", relpos=(0.5, 0.0), fc="w",
    ),
)
ax.plot(
    cnp_x[0], cnp_delays[0], "kD",
)

if signal_setting is not None:
    fig_str = (
        "figs_in_paper/perturb_c=" + str(berth_num) + "_" + queue_rule + "_signal.jpg"
    )
else:
    fig_str = (
        "figs_in_paper/perturb_c=" + str(berth_num) + "_" + queue_rule + "_iso.jpg"
    )
fig.savefig(fig_str)

