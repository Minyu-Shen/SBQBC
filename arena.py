import matplotlib.pyplot as plt
import math

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
            # bus_delay_count += bus.dpt_stop_mmt - bus.arr_mmt - (bus.service_end_mmt - bus.service_start_mmt)
            bus_delay_count += bus.enter_delay
            bus_delay_count += bus.exit_delay
            bus_count += 1
    return bus_delay_count / bus_count*1.0
