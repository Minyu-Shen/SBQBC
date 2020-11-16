import matplotlib.pyplot as plt
from arena import (
    cal_berth_rho_for_each_plan,
    plot_contour_by_lists,
    get_profile_and_df_from_db,
)
import numpy as np
from hyper_parameters import max_tolerance_delay


line_flow, line_service, run_df = get_profile_and_df_from_db(
    berth_num=3, line_num=6, set_no=0
)
# max_tolerance_delay = 1.0e8
x, y, z = [], [], []
for _, row in run_df.iterrows():
    berth_rho = cal_berth_rho_for_each_plan(
        row["assign_plan_str"], line_flow, line_service
    )
    # diff = abs(berth_rho[0] - berth_rho[1])
    print(sum(berth_rho) / len(berth_rho))
    delay = row["delay_seq"][-1]
    # if delay < max_tolerance_delay:
    if delay < 300.0:
        x.append(berth_rho[0])
        y.append(berth_rho[1])
        z.append(delay)

fig = plot_contour_by_lists(x, y, z)
fig.savefig("figs/3_berth_general_view.jpg")

