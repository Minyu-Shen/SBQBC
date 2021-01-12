import matplotlib.pyplot as plt
from plot_settings import get_curve_plot
import numpy as np
from arena import sacred_to_df
from pymongo import MongoClient
import pandas as pd

client = MongoClient("localhost", 27017)
db = client["perturb_stop"]
# collection = db["runs"]

berth_num = 4
line_num = 12
arrival_type = "Gaussian"
queue_rule = "FO-Bus"
signal_setting = None
signal_setting = (120, 0.5, 3)

db_query = {
    "config.queue_rule": queue_rule,
    "config.berth_num": berth_num,
    "config.line_num": line_num,
    "config.arrival_type": arrival_type,
}
if signal_setting is None:
    db_query["config.signal_setting"] = None
else:
    db_query["config.cycle_length"] = signal_setting[0]
    db_query["config.green_ratio"] = signal_setting[1]
    db_query["config.buffer_size"] = signal_setting[2]

df = sacred_to_df(db.runs, db_query)
df["delay"] = df["delay_seq"].apply(lambda x: x[-1] if isinstance(x, list) else None)
### perturb points
perturb_df = df[df["simple_policy_delay"].isna()]
delays = perturb_df["delay"].to_numpy()
min_delays = [delays[0]]  # minimum delay until k
for k in range(1, len(delays), 1):
    min_delays.append(min(min_delays[-1], delays[k]))
sorted_delays = -np.sort(-delays)

### simple-policy points
simple_df = df[df["simple_policy_delay"].notna()]
simple_delay = simple_df["simple_policy_delay"].values[0]
print("the simple delay is:", simple_delay)

### generate figures for each queueing rule
fig, ax = get_curve_plot(
    x_label="Number of randomly-generated allocation plans",
    y_label="Average bus delay in desceding order",
    x_font=15,
    y_font=15,
)

### set range
x = np.arange(1, len(delays) + 1, 1)
x_ticks = [1]
x_ticks.extend(list(np.arange(50, len(sorted_delays) + 1, 50)))

# ### plot
# ax.set_ylim([1, 1.5])
# # ax.set_xlim([1, x_range])
ax.set_xticks(x_ticks)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.set_xlim([1, 500])
ax.set_ylim([35, 180])
ax.plot(
    x,
    sorted_delays,
    linestyle="solid",
    color="k",
    label="random perturbation in descending order",
)
ax.plot(
    x, [simple_delay] * len(x), linestyle="dashed", color="k", label="simple policy"
)

ax.annotate(
    "simple policy",
    xy=(20, simple_delay),
    xytext=(150, simple_delay + 40),
    size=15,
    va="center",
    ha="center",
    bbox=dict(boxstyle="round4", fc="w"),
    arrowprops=dict(
        arrowstyle="->", connectionstyle="arc3,rad=0.0", relpos=(0.0, 0.0), fc="w",
    ),
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

