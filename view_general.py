from pymongo import MongoClient
from sacred_to_df import sacred_to_df
import matplotlib.pyplot as plt
import numpy as np
import ast


def cal_berth_rho_for_each_plan(assign_plan, line_flow, line_service):
    # if assign_plan is a string, covnert it
    assign_plan = (
        ast.literal_eval(assign_plan) if type(assign_plan) == str else assign_plan
    )
    # print(line_flow)
    # print(line_service)
    berth_num = len(set(assign_plan.values()))
    berth_flow = [0.0] * berth_num
    berth_service = [0.0] * berth_num
    for ln, berth in assign_plan.items():
        berth_flow[berth] += line_flow[str(ln)][0]
        berth_service[berth] += line_service[str(ln)][0]
    berth_rho = [(x / 3600.0) * y for x, y in zip(berth_flow, berth_service)]
    return berth_rho


client = MongoClient("localhost", 27017)
db = client["stop"]

query = {"berth_num": 2, "line_num": 6, "set_no": 0}
profile = db.line_profile.find(query)[0]
line_flow, line_service = profile["line_flow"], profile["line_service"]

query = "line_num==6 and berth_num==2"
run_df = sacred_to_df(db.runs).query(query)
fig, ax = plt.subplots()
diffs = []
delays = []
for _, row in run_df.iterrows():
    berth_rho = cal_berth_rho_for_each_plan(
        row["assign_plan_str"], line_flow, line_service
    )
    diff = abs(berth_rho[0] - berth_rho[1])
    diffs.append(diff)
    delay = row["delay_seq"][-1]
    delays.append(delay)
#     # print(assign_plan, delay)

ax.scatter(diffs, delays)
fig.savefig("figs/2_berth_general_view.jpg")

