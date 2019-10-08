from bus_generator import Generator
from dist_stop import DistStop
from intersection import Signal
import numpy as np
import hyper_parameters as paras
from arena import set_x_y_draw
import matplotlib.pyplot as plt

def sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan=None, c_H=1.0):

    ######## hyper-parameters ########
    duration = 3600 * 15

    ######## simulation ########
    # bus_flows = {0: [160.0, 1.0]} # [x:buses/hr, y: c.v.]
    generator = Generator(flows, duration, assign_plan)
    stop = DistStop(0, berth_num, queue_rule, services) # [x:mean_dwell, y: c.v. of dwell]
    total_buses = []
    for t in np.arange(0.0, duration, paras.sim_delta):
        ##### from downstream to upstream #####
        ### operation at the stop ...
        stop.process(t)

        ### dispatch process ...
        if persistent:
            # the capacity case, keep the entry queue length == berth_num
            # print(stop.get_entry_queue_length())
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
    
    if duration < 1800:
        plot_time_space(berth_num, total_buses, duration, paras.sim_delta, stop)
        pass
    # calculate discharing flow and return
    if persistent:
        return stop.exit_counting / (duration*1.0)
    else:
        # calculate delays
        bus_count = 0
        bus_delay_count = 0.0
        for bus in total_buses:
            if bus.dpt_stop_mmt is not None: # only count the buses that have left the stop
                # bus_delay_count += bus.dpt_stop_mmt - bus.arr_mmt - (bus.service_end_mmt - bus.service_start_mmt)
                bus_delay_count += bus.enter_delay
                bus_delay_count += bus.exit_delay
                bus_count += 1
        return bus_delay_count / bus_count*1.0


def plot_time_space(berth_num, total_buses, duration, sim_delta, stop):
    jam_spacing = 10
    colors = ['violet','g','b','y','k','w']
    count = 0
    sorted_list = sorted(total_buses, key=lambda x: x.bus_id, reverse=False)
    # plot the insertion mark
    for berth, times in stop.berth_state.items():
        for i in range(len(times)-1):
            if times[i] == True or times[i+1] == True:
                plt.hlines(berth+1, i*sim_delta, (i+1)*sim_delta, 'r', linewidth=8)

    for bus in sorted_list:
        # print(bus.bus_id)
        j = count % 5
        # if count == 0:
            # j = 5
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
    plt.show()


if __name__ == "__main__":
    ######### parameters ########
    berth_num = 4
    # 'LO-Out','LO-In-Bus','FO-Bus','LO-In-Lane', 'FO-Lane'
    queue_rule = 'FO-Bus'
    f = 160.0 # buses/hr
    mu_S = 25 # seconds
    c_S = 0.4
    c_H = 1 # arrival headway variation
    persistent = False
    assign_plan = {0:0, 1:1, 2:2, 3:3} # line -> berth
    flows = {0: [40, 1.0], 1:[40, 1.0], 2:[40, 1.0], 3:[40, 1.0]} # [buses/hr, c.v.]
    # flows = {0: [160.0, 1.0]}
    # services = {0: [25, 0.4], 1: [25, 0.4], 2: [25, 0.4], 3: [25, 0.4]}

    ######### for plotting time-space diagram ########
    # sim_one_isolated_scenario(berth_num, queue_rule, f, mu_S, c_S, persistent)

    ### plot settings
    line_styles = ['-', ':', '--', '-.', '-.']
    rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane', 'LO-In-Bus']
    rule2style = {rules[i]: line_styles[i] for i in range(len(rules))}

    ######### for desire ########
    # rules = ['FIFO', 'LO-Out']
    # rules = ['FO-Bus']
    # rules = ['FO-Bus', 'FO-Lane']
    # rules = ['FO-Lane']
    # rules = ['LO-Out', 'FO-Bus']
    # rules = ['FIFO', 'LO-Out', 'FO-Bus']
    rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane']
    # rules = ['FIFO', 'LO-Out', 'FO-Lane']
    # rules = ['LO-Out', 'FO-Bus', 'FO-Lane']

    if persistent:
        c_Ss = [0.1*x for x in range(11)]
        rule_capacities = {}
        for queue_rule in rules:
            capacities = []
            for c_S in c_Ss:
                services = {0: [mu_S, c_S]}
                cpt = sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan)
                capacities.append(cpt * 3600.0)
            rule_capacities[queue_rule] = capacities
        print(rule_capacities)

        # plotting ...
        plt, ax = set_x_y_draw('C_S', 'buses/hr')
        for rule, capacities in rule_capacities.items():
            if rule == 'FO-Lane':
                plt.plot(c_Ss, capacities, 'r', linestyle=rule2style[rule], linewidth=2)
            else:
                plt.plot(c_Ss, capacities, 'k', linestyle=rule2style[rule], linewidth=2)
        # ax.legend([r'FIFO', r'LO-Out', r'FO-Bus', r'FO-Lane'],\
            # handlelength=3, fontsize=13)
        plt.show()
    else:
        c_Ss = [0.1*x for x in range(11)]
        rule_delays = {}
        for queue_rule in rules:
            delays = []
            for c_S in c_Ss:
                services = {0: [mu_S, c_S], 1: [mu_S, c_S], 2: [mu_S, c_S], 3: [mu_S, c_S]}
                print(services)
                delay = sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan)
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
