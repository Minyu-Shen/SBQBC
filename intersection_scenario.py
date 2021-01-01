from bus_generator import Generator
from dist_stop import DistStop
from intersection import Signal
import numpy as np
import parameters as paras

# ######## parameters ########
# berth_num = 3
# f = 100.0 # buses/hr
# mu_H = 3600.0 / f # seconds
# mu_S = 25 # seconds
# c_S = 0.4
# c_H = 0.4 # arrival headway variation
# cycle_length = 160
# green_ratio = 0.5
# persistent = True


def sim_one_NS_scenario(
    berth_num,
    queue_rule,
    f,
    mu_S,
    c_S,
    cycle_length,
    green_ratio,
    buffer_size,
    persistent,
    c_H=1.0,
):

    ######## hyper-parameters ########
    duration = 3600 * 50

    ######## simulation ########
    bus_flows = {0: [f, c_H]}  # [x:buses/hr, y: c.v.]
    generator = Generator(bus_flows, duration)

    signal = Signal(cycle_length, green_ratio, buffer_size)
    stop = DistStop(
        0, berth_num, queue_rule, {0: [mu_S, c_S]}, down_signal=signal
    )  # [x:mean_dwell, y: c.v. of dwell]
    # stop = NormalPaxStop(0, berth_num, {0: pax_lambda}) # pax/sec

    total_buses = []
    leaving_count = 0
    for t in np.arange(0.0, duration, paras.sim_delta):
        ### signal queue discharing ...
        signal.discharge(t)

        ### dispatch process ...
        if persistent:
            # the capacity case, keep the entry queue length >= 3
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

        ### operation at the first stop ...
        stop.operation(t)

    # calculate mean
    # delays = []
    # for bus in total_buses:
    # print(bus.arr_time, bus.etr_time, bus.dpt_time)
    # delays.append(bus.enter_delay + bus.exit_delay)
    # delays = np.array(delays)
    # print(delays.mean())

    # calculate discharing flow and return
    return stop.leaving_count / (duration * 1.0)

