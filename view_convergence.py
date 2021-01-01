from pymongo import MongoClient
from sacred_to_df import sacred_to_df
import matplotlib.pyplot as plt
import numpy as np
from hyper_parameters import max_tolerance_delay

client = MongoClient("localhost", 27017)
db = client["near_stop"]
queue_rule = "FIFO"
query = "berth_num == 2 and line_num == 10 and queue_rule == @queue_rule"
# db = client["near_stop"]
# query = "line_num == 6"

df = sacred_to_df(db.runs).query(query)

fig, ax = plt.subplots()
for idx, row in df.iterrows():
    delay_seq = row["delay_seq"]
    # ax.plot(delay_seq)
    eval_num = 20
    std_list = []
    cv_list = []
    # if delay_seq[-1] >= max_tolerance_delay:
    if delay_seq[-1] >= 100:
        continue
    round_num = int(len(delay_seq) / eval_num)
    # for i in range(len(delay_seq) - eval_num):
    for i in range(round_num):
        eval_seq = np.array(delay_seq[i * eval_num : (i + 1) * eval_num])
        std = np.std(eval_seq)
        cv = std / np.mean(eval_seq)
        std_list.append(std)
        cv_list.append(cv)
    xs = [(x + 1) * eval_num for x in range(round_num)]
    ax.plot(delay_seq, color="r")
    # ax2 = ax.twinx()
    # ax2.plot(xs, cv_list)
    print(std_list)


# fig.savefig("figs/seq_no_assign.jpg")
fig.savefig("figs/seq.jpg")
