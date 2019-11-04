from bus_generator import Generator
from dist_stop import DistStop
from signal import Signal, Buffer
# from queue import Buffer
import hyper_parameters as paras
from arena import set_x_y_draw
import matplotlib.pyplot as plt
from arena import calculate_avg_delay, calculate_list_std

def sim_one_NS_scenario(berth_num, queue_rule, flows, services, persistent, buffer_size, cycle_length, green_ratio, assign_plan=None):

    ######## hyper-parameters ########
    eval_every = 3600 * 5
    duration = eval_every * 5 # the number of epochs
    check_no = 5
    threshold = 0.5 # for convergence check

    ######## simulation ########
    generator = Generator(flows, duration, assign_plan)
    down_signal = Signal(cycle_length, green_ratio)
    down_buffer = Buffer(buffer_size, down_signal)
    stop = DistStop(0, berth_num, queue_rule, services, down_buffer, None) # [x:mean_dwell, y: c.v. of dwell]
    total_buses = []
    mean_seq = []
    # duration = int(3600 * 0.2)
    for epoch in range(0, duration, 1):
        t = epoch * paras.sim_delta
        ##### from downstream to upstream #####
        ### operation in the buffer

        ### operation at the stop ...
        stop.process(t)

        ### dispatch process ...
        if persistent:
            # the capacity case, keep the entry queue length == berth_num
            while stop.get_entry_queue_length() < berth_num:
                bus = generator.dispatch(t, persistent=True)
                total_buses.append(bus)
                stop.bus_arrival(bus, t)
        else:
            # according to arrival table
            dispatched_buses = generator.dispatch(t)
            # directly added to the first stop
            for bus in dispatched_buses:
                total_buses.append(bus)
                stop.bus_arrival(bus, t)

        ### evaluate the convergence
        if epoch % eval_every == 0 and epoch != 0:
            if persistent:
                mean_seq.append(stop.exit_counting / (t*1.0) * 3600)
            else:
                mean_seq.append(calculate_avg_delay(total_buses))
                # print(mean_seq)
            if len(mean_seq) >= check_no: # at least
                mean_seq_std = calculate_list_std(mean_seq[-check_no:])
                if mean_seq_std < threshold: return mean_seq[-1]
        

    if duration < 1800:
        plot_NS_time_space(berth_num, total_buses, duration, paras.sim_delta, stop, down_buffer, down_signal)

    return mean_seq[-1]


def plot_NS_time_space(berth_num, total_buses, duration, sim_delta, stop, down_buffer, down_signal):
    colors = ['r','g','b','y','k','w']
    count = 0
    sorted_list = sorted(total_buses, key=lambda x: x.bus_id, reverse=False)
    # plot the insertion mark
    for berth, times in stop.berth_state.items():
        for i in range(len(times)-1):
            if times[i] == True or times[i+1] == True:
                plt.hlines(berth+1, i*sim_delta, (i+1)*sim_delta, 'r', linewidth=8)

    # print(len(sorted_list))
    for bus in sorted_list:
        j = count % 5
        # j = bus.assign_berth
        lists = sorted(bus.trajectory_locations.items()) # sorted by key, return a list of tuples
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        x_list = list(x)
        y_list = list(y)
        for i in range(len(x)-1):
            y_1 = y_list[i]-10 if y_list[i] > 8 else y_list[i]
            y_2 = y_list[i+1]-10 if y_list[i+1] > 8 else y_list[i+1]
            y_tuple = (y_1, y_2)
            x_tuple = (x_list[i], x_list[i+1])

            if y_list[i+1] > 8:
               plt.plot(x_tuple, y_tuple, colors[j], linestyle='dotted', linewidth=1)
            else:
                plt.plot(x_tuple, y_tuple, colors[j])
        # plot the service time
        if bus.service_berth is not None:
            plt.hlines((bus.service_berth+1), bus.service_start_mmt, bus.service_end_mmt, 'gray', linewidth=5)
        
        count += 1

    # plot signal
    C = down_signal._cycle_length
    G = down_signal._green_ratio * C
    R = C-G
    for i in range(int(duration) // C):
        # plot green period
        plt.hlines(berth_num+1+down_buffer.buffer_size, i*C, i*C+G, linewidth=2.5, colors='g')
        # plot red period
        plt.hlines(berth_num+1+down_buffer.buffer_size, i*C+G, (i+1)*C, linewidth=2.5, colors='r')

    # plot buffer

    plt.show()


if __name__ == "__main__":
    ######### parameters ########
    cycle_length = 140
    green_ratio = 0.5
    buffer_size = 0

    berth_num = 4
    # 'LO-Out','LO-In-Bus','FO-Bus','LO-In-Lane', 'FO-Lane'
    queue_rule = 'FO-Bus'
    # queue_rule = 'FIFO'
    mu_S = 25 # seconds
    c_S = 0.4
    c_H = 1 # arrival headway variation
    persistent = True

    f = 140.0 # buses/hr
    # assign_plan = {0:0, 1:1, 2:2, 3:3} # line -> berth
    assign_plan = None
    flows = {0: [f/4, 1.0], 1:[f/4, 1.0], 2:[f/4, 1.0], 3:[f/4, 1.0]} # [buses/hr, c.v.]
    # flows = {0: [160.0, 1.0]}
    services = {0: [mu_S, c_S], 1: [mu_S, c_S], 2: [mu_S, c_S], 3: [mu_S, c_S]}

    ######### for plotting time-space diagram ########
    # res = sim_one_NS_scenario(berth_num, queue_rule, flows, services, persistent, buffer_size, cycle_length, green_ratio, assign_plan)

    ### plot settings
    line_styles = ['-', ':', '--', '-.', '-.']
    rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane', 'LO-In-Bus']
    rule2style = {rules[i]: line_styles[i] for i in range(len(rules))}

    ######## for desire ########
    rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane']
    # rules = ['FO-Bus']

    if persistent:
        c_Ss = [0.1*x for x in range(11)]
        rule_capacities = {}
        for queue_rule in rules:
            capacities = []
            for c_S in c_Ss:
                print(c_S)
                services = {0: [mu_S, c_S]}
                cpt = sim_one_NS_scenario(berth_num, queue_rule, flows, services, persistent, buffer_size, cycle_length, green_ratio, assign_plan)
                capacities.append(cpt)
            rule_capacities[queue_rule] = capacities
        print(rule_capacities)

        # plotting ...
        plt, ax = set_x_y_draw('C_S', 'buses/hr')
        for rule, capacities in rule_capacities.items():
            if rule == 'FO-Bus':
                plt.plot(c_Ss, capacities, 'r', linestyle=rule2style[rule], linewidth=2)
            else:
                plt.plot(c_Ss, capacities, 'k', linestyle=rule2style[rule], linewidth=2)
        ax.legend([r'FIFO', r'LO-Out', r'FO-Bus', r'FO-Lane'], handlelength=3, fontsize=13)
        plt.show()
    else:
        c_Ss = [0.1*x for x in range(11)]
        rule_delays = {}
        for queue_rule in rules:
            delays = []
            for c_S in c_Ss:
                services = {0: [mu_S, c_S], 1: [mu_S, c_S], 2: [mu_S, c_S], 3: [mu_S, c_S]}
                print(c_S)
                delay = sim_one_NS_scenario(berth_num, queue_rule, flows, services, persistent, buffer_size, cycle_length, green_ratio, assign_plan)
                delays.append(delay)
            rule_delays[queue_rule] = delays
        print(rule_delays)

        # plotting ...
        plt, ax = set_x_y_draw('C_S', 'delay (secs)')
        for rule, delays in rule_delays.items():
            if rule == 'FO-Lane':
                plt.plot(c_Ss, delays, 'r', linestyle=rule2style[rule], linewidth=2)
            else:
                plt.plot(c_Ss, delays, 'k', linestyle=rule2style[rule], linewidth=2)

        ax.legend(rules, handlelength=3, fontsize=13)

        plt.show()
