from pymongo import MongoClient
from sacred_to_df import sacred_to_df
import matplotlib.pyplot as plt
import numpy as np

client = MongoClient("localhost", 27017)
db = client["stop"]

query = "line_num == 4"
df = sacred_to_df(db.runs).query(query)
# print(df.columns)

fig, ax = plt.subplots()
for _, row in df.iterrows():
    delay_seq = row["delay_seq"]
    # ax.plot(delay_seq)
    eval_num = 20
    std_list = []
    cv_list = []
    round_num = int(len(delay_seq) / eval_num)
    # for i in range(len(delay_seq) - eval_num):
    for i in range(round_num):
        eval_seq = np.array(delay_seq[i * eval_num : (i + 1) * eval_num])
        std = np.std(eval_seq)
        cv = std / np.mean(eval_seq)
        std_list.append(std)
        cv_list.append(cv)
    xs = [(x + 1) * eval_num for x in range(round_num)]
    ax.plot(xs, cv_list)
    print(std_list)
    ax2 = ax.twinx()
    ax2.plot(delay_seq, color="r")


# fig.savefig("figs/seq_no_assign.jpg")
fig.savefig("figs/seq.jpg")
