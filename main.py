from intersection_scenario import sim_one_NS_scenario
import matplotlib.pyplot as plt

######## parameters ########
berth_num = 2
queue_rule = "FIFO"
f = 100.0  # buses/hr
mu_S = 25  # seconds
c_S = 0.1
c_H = 0.4  # arrival headway variation
# cycle_length = 160
green_ratio = 0.5
buffer_size = 0
persistent = True

cycle_lengths = list(range(80, 241, 10))
capacities = []
for cycle_length in cycle_lengths:
    capacity = sim_one_NS_scenario(
        berth_num,
        queue_rule,
        f,
        mu_S,
        c_S,
        cycle_length,
        green_ratio,
        buffer_size,
        persistent,
    )
    capacities.append(capacity * 3600.0)

plt.plot(cycle_lengths, capacities)
