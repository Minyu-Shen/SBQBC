from bus_generator import Generator
from dist_stop import DistStop
from intersection import Signal
import numpy as np
import hyper_parameters as paras
from arena import set_x_y_draw
import matplotlib.pyplot as plt

def sim_one_isolated_scenario(berth_num, queue_rule, f, mu_S, c_S, persistent, c_H=1.0):

    ######## hyper-parameters ########
    duration = 3600 * 0.1

    ######## simulation ########
    bus_flows = {0: [f, c_H]} # [x:buses/hr, y: c.v.]
    generator = Generator(bus_flows, duration)
    stop = DistStop(0, berth_num, queue_rule, {0: [mu_S, c_S]}) # [x:mean_dwell, y: c.v. of dwell]
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
    
    plot_time_space(berth_num, total_buses, duration, paras.sim_delta)
    # calculate discharing flow and return
    return stop.exit_counting / (duration*1.0)


def plot_time_space(berth_num, total_buses, duration, sim_delta):
    jam_spacing = 10
    for bus in total_buses:
        plt.plot(bus.lane_trajectory_times, [x * jam_spacing for x in bus.lane_trajectory], 'gray', linestyle='dashed', linewidth=4)
        plt.plot(bus.trajectory_times, [x * jam_spacing for x in bus.trajectory])
        
        # plot the service time
        if bus.service_berth is not None:
            plt.hlines((bus.service_berth+1)*jam_spacing, bus.service_start, bus.service_end, linewidth=5)

    for b in range(berth_num):
        plt.hlines((b+1)*jam_spacing,0,duration, linestyles='dotted')
    
    plt.show()


if __name__ == "__main__":

    ######### parameters ########
    berth_num = 2
    # 'LO-Out','LO-In-Bus','FO-Bus','LO-In-Lane', 'FO-Lane'
    # queue_rule = 'LO-Out'
    # queue_rule = 'FIFO'
    queue_rule = 'FO-Bus'
    f = 100.0 # buses/hr
    mu_S = 25 # seconds
    c_S = 0
    c_H = 0.4 # arrival headway variation
    persistent = True

    ######### for plotting time-space diagram ########
    sim_one_isolated_scenario(berth_num, queue_rule, f, mu_S, c_S, persistent)
    ######### for plotting time-space diagram ########


    ######### for desired setting ########
    # c_Ss = [0.3, 0.4]

    # c_Ss = [0.1*x for x in range(11)]

    # rules = ['FIFO', 'LO-Out']
    # # rules = ['FO-Bus']
    # # rules = ['FIFO', 'LO-Out', 'FO-Bus']

    # rule_capacities = {}
    # for queue_rule in rules:
    #     capacities = []
    #     for c_S in c_Ss:
    #         print(c_S)
    #         cpt = sim_one_isolated_scenario(berth_num, queue_rule, f, mu_S, c_S, persistent)
    #         capacities.append(cpt * 3600.0)
    #     rule_capacities[queue_rule] = capacities
    # print(rule_capacities)

    # # plotting ...
    # plt, ax = set_x_y_draw('C_S', 'buses/hr')
    # line_styles = ['-', '--', ':', '-.']
    # rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane']
    # rule2style = {rules[i]: line_styles[i] for i in range(len(rules))}

    # for rule, capacities in rule_capacities.items():
    #     plt.plot(c_Ss, capacities, 'k', linestyle=rule2style[rule], linewidth=2)

    # ax.legend([r'FIFO', r'LO-Out', r'FO-Bus', r'FO-Lane'],\
    #     handlelength=3, fontsize=13)

    # plt.show()
