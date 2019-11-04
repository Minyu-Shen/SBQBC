import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import permutations, combinations, product

def set_x_y_draw(x_label, y_label):
    # draw settings
    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.grid(linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=11)

    return plt, ax

def calculate_list_std(data_list):
    mean = sum(data_list) / len(data_list)
    std = math.sqrt(sum([(xi - mean)**2 for xi in data_list]) / (len(data_list) -1))
    return std

def calculate_avg_delay(total_buses):
    # calculate delays
    bus_count = 0
    bus_delay_count = 0.0
    for bus in total_buses:
        if bus.dpt_stop_mmt is not None: # only count the buses that have left the stop
            bus_delay_count += (bus.dpt_stop_mmt - bus.arr_mmt - bus.total_service_time)
            # bus_delay_count += bus.enter_delay
            # bus_delay_count += bus.exit_delay
            bus_count += 1
    return bus_delay_count / bus_count*1.0

def generate_line_info(line_no, total_arrival, mean_service, arrival_cvs=(0.4,0.6), service_cvs=(0.4,0.6)):
    '''
    total_arrival - buses/hr
    mean_service - seconds
    '''
    # arrival line infos
    arr_scale = 5 # larger scale, smaller variance of arrival flow mean
    arr_flows = np.random.dirichlet(np.ones(line_no)*arr_scale, size=1).squeeze() * total_arrival

    # service line infors
    service_scale = 20 # larger scale, smaller variance of service mean
    service_means = np.random.dirichlet(np.ones(line_no)*service_scale, size=1).squeeze() * mean_service * line_no
    flow_infos = {}
    service_infos = {}

    for i in range(line_no):
        arr_cv = arrival_cvs[0] if arrival_cvs[0] == arrival_cvs[1] else np.random.uniform(arrival_cvs[0], arrival_cvs[1])
        flow_infos[i] = (arr_flows[i], arr_cv)
        service_cv = service_cvs[0] if service_cvs[0] == service_cvs[1] else np.random.uniform(service_cvs[0], service_cvs[1])
        service_infos[i] = (service_means[i], service_cv)
        
    return flow_infos, service_infos


def assign_plan_enumerator(line_no, berth_num, flow_infos, service_infos):
    berths = [i for i in range(berth_num)]
    for roll in product(berths, repeat = line_no): # roll is a tuple
        if len(set(roll)) == berth_num: # all berths should be assigned at least one line
            yield {l: roll[l] for l in range(line_no)}
            
def make_assign_plan(line_no, berth_num, flow_infos, service_infos):
    berths = [i for i in range(berth_num)]
    plans = []
    for roll in product(berths, repeat = line_no): # roll is a tuple
        if len(set(roll)) == berth_num: # all berths should be assigned at least one line
            plans.append({l: roll[l] for l in range(line_no)})

    return plans

if __name__ == "__main__":
    flow_infos, service_infos = generate_line_info(4, 140, 25, arrival_cvs=(0.6,0.6), service_cvs=(0.4,0.6))
    print(flow_infos, service_infos)
    # for i in assign_plan_enumerator(3,2,4,4):
        # print(i)
