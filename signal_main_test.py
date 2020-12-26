from signal_scenario import sim_one_NS_scenario
from arena import set_x_y_draw


######### parameters ########
cycle_length = 140
green_ratio = 0.5
buffer_size = 4

berth_num = 2
mu_S = 25  # seconds
c_S = 0.4
c_H = 1  # arrival headway variation
is_persistent = True
is_persistent = False

f = 120.0  # buses/hr
# assign_plan = {0:0, 1:1, 2:2, 3:3} # line -> berth
assign_plan = None
flows = {
    0: [f / 4, 1.0],
    1: [f / 4, 1.0],
    2: [f / 4, 1.0],
    3: [f / 4, 1.0],
}  # [buses/hr, c.v.]
# flows = {0: [160.0, 1.0]}
# services = {0: [mu_S, c_S], 1: [mu_S, c_S], 2: [mu_S, c_S], 3: [mu_S, c_S]}

######### for plotting time-space diagram ########
# res = sim_one_NS_scenario(berth_num, queue_rule, flows, services, persistent, buffer_size, cycle_length, green_ratio, assign_plan)

### plot settings
line_styles = ["-", ":", "--", "-.", "-."]
rules = ["FIFO", "LO-Out", "FO-Bus", "FO-Lane", "LO-In-Bus"]
rule2style = {rules[i]: line_styles[i] for i in range(len(rules))}

######## for desire ########
rules = ["FIFO", "LO-Out", "FO-Bus", "FO-Lane"]
# rules = ['FO-Bus']

if is_persistent:
    c_Ss = [0.1 * x for x in range(11)]
    rule_capacities = {}
    for queue_rule in rules:
        capacities = []
        for c_S in c_Ss:
            print("persistent case, C_S is: ", c_S)
            services = {0: [mu_S, c_S]}
            cpt = sim_one_NS_scenario(
                berth_num,
                queue_rule,
                flows,
                services,
                is_persistent,
                buffer_size,
                cycle_length,
                green_ratio,
                assign_plan,
            )[-1]
            capacities.append(cpt)
            rule_capacities[queue_rule] = capacities
        print(rule_capacities)

    # plotting ...
    fig, ax = set_x_y_draw("C_S", "buses/hr")
    for rule, capacities in rule_capacities.items():
        if rule == "FO-Bus":
            ax.plot(c_Ss, capacities, "r", linestyle=rule2style[rule], linewidth=2)
        else:
            ax.plot(c_Ss, capacities, "k", linestyle=rule2style[rule], linewidth=2)
    ax.legend([r"FIFO", r"LO-Out", r"FO-Bus", r"FO-Lane"], handlelength=3, fontsize=13)
    fig_str = (
        "figs/C="
        + str(cycle_length)
        + "_c="
        + str(berth_num)
        + "_d="
        + str(buffer_size)
        + "_cap_case.jpg"
    )
    fig.savefig(fig_str)
else:
    c_Ss = [0.1 * x for x in range(11)]
    rule_delays = {}
    for queue_rule in rules:
        delays = []
        for c_S in c_Ss:
            services = {
                0: [mu_S, c_S],
                1: [mu_S, c_S],
                2: [mu_S, c_S],
                3: [mu_S, c_S],
            }
            print("delay case, C_S is: ", c_S)
            delay = sim_one_NS_scenario(
                berth_num,
                queue_rule,
                flows,
                services,
                is_persistent,
                buffer_size,
                cycle_length,
                green_ratio,
                assign_plan,
            )[-1]
            delays.append(delay)
        rule_delays[queue_rule] = delays
    print(rule_delays)

    # plotting ...
    fig, ax = set_x_y_draw("C_S", "delay (secs)")
    for rule, delays in rule_delays.items():
        if rule == "FO-Lane":
            ax.plot(c_Ss, delays, "r", linestyle=rule2style[rule], linewidth=2)
        else:
            ax.plot(c_Ss, delays, "k", linestyle=rule2style[rule], linewidth=2)
    ax.legend(rules, handlelength=3, fontsize=13)
    fig_str = (
        "figs/C="
        + str(cycle_length)
        + "_c="
        + str(berth_num)
        + "_d="
        + str(buffer_size)
        + "_delay_case.jpg"
    )
    fig.savefig(fig_str)
