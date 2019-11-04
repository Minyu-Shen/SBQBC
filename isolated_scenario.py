from bus_generator import Generator
from dist_stop import DistStop
import numpy as np
import hyper_parameters as paras
import matplotlib.pyplot as plt
from arena import calculate_avg_delay, calculate_list_std, generate_line_info, assign_plan_enumerator, make_assign_plan, set_x_y_draw
from multiprocessing import Pool, cpu_count, Process
import concurrent.futures
import pickle
import time

# def sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan):
def sim_one_isolated_scenario(*args):
    berth_num, queue_rule, flows, services, persistent, assign_plan = args[0]
    # print('......', assign_plan)
    ######## hyper-parameters ########
    eval_every = 3600 * 10
    duration = eval_every * 20 # the number of epochs
    check_no = 5
    threshold = 0.25 # for convergence check

    ######## simulation ########
    generator = Generator(flows, duration, assign_plan)
    stop = DistStop(0, berth_num, queue_rule, services, None, None) # [x:mean_dwell, y: c.v. of dwell]
    total_buses = []
    mean_seq = []
    # duration = int(3600 * 0.1)
    for epoch in range(0, duration, 1):
        t = epoch * paras.sim_delta
        ##### from downstream to upstream #####
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
                if mean_seq_std < threshold: return (assign_plan, mean_seq[-1])
        

    if duration < 1800:
        plot_time_space(berth_num, total_buses, duration, paras.sim_delta, stop)
    # print((assign_plan, mean_seq[-1]))
    return (assign_plan, mean_seq[-1])


def plot_time_space(berth_num, total_buses, duration, sim_delta, stop):
    jam_spacing = 10
    colors = ['r','g','b','y','k','w']
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
    plt.show()


def testing():
    ######### parameters ########
    berth_num = 4
    f = 140.0 # buses/hr
    mu_S = 25 # seconds
    line_no = 4
    persistent = False
    assign_plan = {0:0, 1:1, 2:2, 3:3} # line -> berth
    # assign_plan = None
    flows, services = generate_line_info(line_no, f, mu_S)

    # flows = {0: [f/4, 1.0], 1:[f/4, 1.0], 2:[f/4, 1.0], 3:[f/4, 1.0]} # [buses/hr, c.v.]
    # services = {0: [mu_S, c_S], 1: [mu_S, c_S], 2: [mu_S, c_S], 3: [mu_S, c_S]}

    ######### for plotting time-space diagram ########
    # queue_rule = 'FO-Bus'
    # res = sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan)

    ### plot settings
    line_styles = ['-', ':', '--', '-.']
    rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane']
    rule2style = {rules[i]: line_styles[i] for i in range(len(rules))}

    ######### for desire ########
    # rules = ['FIFO', 'LO-Out', 'FO-Bus', 'FO-Lane']
    rules = ['FIFO', 'LO-Out', 'FO-Bus']

    if persistent:
        c_Ss = [0.1*x for x in range(11)]
        rule_capacities = {}
        for queue_rule in rules:
            capacities = []
            for c_S in c_Ss:
                print(c_S)
                services = {0: [mu_S, c_S]}
                cpt = sim_one_isolated_scenario(berth_num, queue_rule, flows, services, persistent, assign_plan)
                capacities.append(cpt)
            rule_capacities[queue_rule] = capacities
        print(rule_capacities)

        # plotting ...
        plt, ax = set_x_y_draw('C_S', 'buses/hr')
        for rule, capacities in rule_capacities.items():
            if rule == 'FO-Lane':
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

    

if __name__ == "__main__":
    # testing()
    np.random.seed(0)
    berth_num = 2
    queue_rule = 'FIFO'
    f = 140.0 # buses/hr
    mu_S = 25 # seconds
    line_no = 3


    for case in range(1):
        flows, services = generate_line_info(line_no, f, mu_S)
        # print(flows, services)

        # assign_plan = None
        # delay = sim_one_isolated_scenario(berth_num, queue_rule, flows, services, False, assign_plan)
        # print(case, assign_plan, delay)
        results = []
        all_plans = make_assign_plan(line_no, berth_num, flows, services)
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            args = ((berth_num, queue_rule, flows, services, False, assign_plan) for assign_plan in all_plans)
            for result in executor.map(sim_one_isolated_scenario, args):
                # plan, delay = result
                results.append(result)
        
        with open('test.pkl', 'wb') as f:
            pickle.dump([results, flows, services], f)


    # with open('test.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
        # results, flows, services = pickle.load(f)
        # print(results)