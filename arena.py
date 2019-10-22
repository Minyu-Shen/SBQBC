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



# def enter_target_update(bus, enter_stop): # bus is the bus to be checked
#     bus_in_upstream_berth = enter_stop._buses_in_berth[0]
#     if bus_in_upstream_berth is None or bus_in_upstream_berth.move_up_step > 0:
#         bus.is_moving_target_set = True
#         bus.berth_target = 0
#         bus.lane_target = None
#         bus.wish_berth = None
#         bus.react_left_step = 0 if bus_in_upstream_berth is None else max(bus.REACT_STEPS - bus_in_upstream_berth.move_up_step, 0)
#         return
#     else: # the bus in the upstream berth will be still
#         # check if can overtake into the berth
#         head_bus_can_move = False
#         if enter_stop._queue_rule in ['LO-In-Bus', 'FO-Bus', 'FO-Lane', 'LO-In-Lane']:
#             bus_in_upstream_place = enter_stop._place_buses_running[0]
#             if bus_in_upstream_place == None or bus_in_upstream_place.move_up_step > 0:
#                 for b in range(enter_stop._berth_num-1, 0, -1):
#                     can_ot_in = check_ot_in_berth_from_queue(enter_stop, b)
#                     if can_ot_in == True:
#                         if bus.assign_berth is None or b == bus.assign_berth:
#                             head_bus_can_move = True
#                             bus.berth_target = None
#                             bus.lane_target = 0
#                             bus.wish_berth = b
#                             enter_stop._remove_old_mark(bus)
#                             enter_stop._order_marks[b] = bus
#                             bus.is_moving_target_set = True
#                             bus.react_left_step = bus.REACT_STEPS if bus_in_upstream_place == None else max(bus.REACT_STEPS - bus_in_upstream_place.move_up_step, 0)
#                             # return b
#                             break

#         if head_bus_can_move == False:
#             bus.lane_target = None
#             bus.berth_target = None
#             # return None

# def check_ot_in_berth_from_queue(enter_stop, check_berth):
#     bus_in_berth = enter_stop._buses_in_berth[check_berth]
#     bus_heading_to_berth = enter_stop._pre_occupies[check_berth]
#     order_by_bus = enter_stop._order_marks[check_berth]
#     if bus_in_berth == None:
#         if bus_heading_to_berth == None and order_by_bus == None:
#             return True
#         else: # the entry queue has the lowest 'grab' power, no need to check 'grab'
#             return False
#     else: # the berth is not empty
#         # if bus_in_berth.is_moving_target_set == False:
#         if bus_in_berth.move_up_step == 0:
#             return False
#         else:
#             if bus_heading_to_berth == None and order_by_bus == None:
#                 return True
#             else:
#                 return False

# def enter_operation(current_time, bus, enter_stop):
#     if bus.lane_target is not None:
#         assert bus.wish_berth is not None, 'enter the lane only when there is available wish berth'
#         assert bus.lane_target == 0, 'the lane target must be the most-upstream place'
#         if bus.react_left_step > 0:
#             bus.react_left_step -= 1
#         else:
#             if bus.move_up_step == 0:
#                 enter_stop._place_pre_occupies[0] = bus
#                 bus.move_up_step += 1
#             else:
#                 bus.move_up_step += 1
#             if bus.move_up_step == bus.MOVE_UP_STEPS:
#                 # already maneuver into the place
#                 bus = enter_stop._entry_queue.pop_one_bus(current_time)
#                 enter_stop._place_buses_running[0] = bus
#                 enter_stop._place_pre_occupies[0] = None
#                 enter_stop.reset_bus_state(bus)
#     else: # lane target is None, only FIFO in
#         if bus.berth_target is not None:
#             assert bus.wish_berth is None, 'no wish berth to overtake in'
#             assert bus.berth_target == 0, 'must be the first berth'
#             # first check the reaction time
#             if bus.react_left_step > 0:
#                 bus.react_left_step -= 1
#             else: # reaction finish, move up
#                 if bus.move_up_step == 0:
#                     enter_stop._pre_occupies[0] = bus
#                     bus.move_up_step += 1
#                 else:
#                     bus.move_up_step += 1
#                 if bus.move_up_step == bus.MOVE_UP_STEPS:
#                     # already maneuver into the place
#                     bus = enter_stop._entry_queue.pop_one_bus(current_time)
#                     enter_stop._buses_in_berth[0] = bus
#                     enter_stop._pre_occupies[0] = None
#                     enter_stop.reset_bus_state(bus)
#         else: # both lane and berth target is not set
#             pass
