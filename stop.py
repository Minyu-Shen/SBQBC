import hyper_parameters as paras
from queue import WaveQueue
# 'process' for methods for sub-stop
# 'operation' for methods in parent-stop
class Stop(object):
    # stop_num = 0
    SIM_DELTA = paras.sim_delta
    MOVE_UP_STEPS = paras.move_up_steps
    REACT_STEPS = paras.reaction_steps

    def __init__(self, stop_id, berth_num, queue_rule, down_signal=None):
        self._stop_id = stop_id
        self._berth_num = berth_num
        self._queue_rule = queue_rule
        self._downstream_signal = down_signal

        # running states for berths
        self._entry_queue = WaveQueue()
        self._buses_in_berth = [None] * berth_num # moving buses that are not fully occupying the whole berth
        self._buses_serving = [None] * berth_num # for service time update
        self._insertion_marks = [False] * berth_num # for cut-in
        self._pre_occupies = [None] * berth_num # the head running in the berth
        self._order_marks = [None] * berth_num # ordered by which berth?

        # running states for lanes
        self._place_buses_running = [None] * berth_num # moving buses that are not fully occupying the whole place
        self._place_pre_occupies = [None] * berth_num # the head running in the berth
        self._place_order_marks = [None] * berth_num

        # stats
        self.exit_counting = 0 # observer at the exit of stop
        self.current_time = 0
        

    def get_entry_queue_length(self):
        return self._entry_queue.get_queue_length()

    # callable methods outside, to add bus into the stop
    def bus_arrival(self, bus, t):
        self._entry_queue.enter_one_bus(bus)

    def reset_bus_state(self, bus):
        bus.react_left_step = None
        bus.berth_target = None
        bus.lane_target = None
        bus.move_up_step = 0
        bus.is_moving_target_set = False

    ########################## time-space info ##########################
    def update_time_space(self, current_time):
        
        for bus in self._entry_queue._buses:
            bus.trajectory_locations[current_time] = 0
        for b in range(self._berth_num):
            bus = self._buses_in_berth[b]
            if bus is None: continue
            bus.trajectory_locations[current_time] = b + 1
            # if bus.bus_id == 9:
            #     print('in the berth', bus.wish_berth, bus.serv_time)
        for place in range(self._berth_num):
            bus = self._place_buses_running[place]
            if bus is None: continue
            bus.trajectory_locations[current_time] = 11 + place
            # if bus.bus_id == 9:
                # print('in the lane', bus.bus_id)

    ########################## operations ##########################

    def _berth_discharge_to_buffer(self):
        self.exit_counting += 1
        # self._buses_in_berth[self._berth_num-1].is_moving_target_set = False
        self._buses_in_berth[self._berth_num-1] = None
        self._insertion_marks[self._berth_num-1] = False
        
    def _lane_discharge_to_buffer(self):
        # self._place_buses_running[self._berth_num-1].is_moving_target_set = False
        self._place_buses_running[self._berth_num-1] = None
        self.exit_counting += 1

    def _entry_queue_operation(self, current_time):
        if self._entry_queue.get_queue_length() == 0: return
        bus = self._entry_queue.get_head_bus(current_time)
        if bus is None: return

        if bus.lane_target is not None:
            assert bus.wish_berth is not None, 'enter the lane only when there is available wish berth'
            assert bus.lane_target == 0, 'the lane target must be the most-upstream place'
            if bus.react_left_step > 0:
                bus.react_left_step -= 1
            else:
                if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                    self._place_pre_occupies[0] = bus
                    bus.move_up_step += 1
                if bus.move_up_step == bus.MOVE_UP_STEPS:
                    # already maneuver into the place
                    bus = self._entry_queue.pop_one_bus(current_time)
                    self._place_buses_running[0] = bus
                    self._place_pre_occupies[0] = None
                    self.reset_bus_state(bus)
        else: # lane target is None, only FIFO in
            if bus.berth_target is not None:
                assert bus.wish_berth is None, 'no wish berth to overtake in'
                assert bus.berth_target == 0, 'must be the first berth'
                # first check the reaction time
                if bus.react_left_step > 0:
                    bus.react_left_step -= 1
                else: # reaction finish, move up
                    if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                        self._pre_occupies[0] = bus
                        bus.move_up_step += 1
                    if bus.move_up_step == bus.MOVE_UP_STEPS:
                        # already maneuver into the place
                        bus = self._entry_queue.pop_one_bus(current_time)
                        self._buses_in_berth[0] = bus
                        self._pre_occupies[0] = None
                        self.reset_bus_state(bus)
            else: # both lane and berth target is not set
                pass

        # self._update_enter_delay()

    def _lane_operation(self, loc):
        bus = self._place_buses_running[loc]
        if bus is None: return
        if loc == (self._berth_num-1):
            # in future add reaction time if there is buffer
            # if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
            #     bus.move_up_step += 1
            # if bus.move_up_step == bus.MOVE_UP_STEPS:

            # for now, just leave, in future, add signal
            assert self._downstream_signal == None
            self._lane_discharge_to_buffer()
        else:
            # not the most-downstream space ...
            if bus.wish_berth is not None: # overtake-in case
                assert self._queue_rule in ['LO-In-Bus','LO-In-Lane','FO-Bus','FO-Lane'], 'must be these rules'
                assert bus.wish_berth > loc, 'wish berth must be greater than current location'
                if bus.berth_target is not None:
                    assert bus.berth_target == loc+1, 'must be the next berth'
                    if bus.react_left_step > 0:
                        bus.react_left_step -= 1
                    else:
                        if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                            self._pre_occupies[bus.berth_target] = bus
                            self._order_marks[bus.berth_target] = None
                            self._insertion_marks[bus.berth_target] = True
                            bus.move_up_step += 1
                        if bus.move_up_step == bus.MOVE_UP_STEPS: # has already reached the next berth
                            self._place_buses_running[loc] = None
                            self._pre_occupies[bus.berth_target] = None
                            self._buses_in_berth[bus.berth_target] = bus
                            self.reset_bus_state(bus)
                            if bus.wish_berth == loc+1:
                                bus.wish_berth = None
                            # self._buses_serving[loc+1] = bus
                else: # cannot enter the berth
                    if bus.lane_target == loc+1: # move the next place
                        if bus.react_left_step > 0:
                            bus.react_left_step -= 1
                        else:
                            if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                                self._place_pre_occupies[bus.lane_target] = bus
                                self._place_order_marks[loc+1] = None
                                bus.move_up_step += 1
                            if bus.move_up_step == bus.MOVE_UP_STEPS:
                                self._place_buses_running[loc] = None
                                self._place_pre_occupies[bus.lane_target] = None
                                self._place_buses_running[bus.lane_target] = bus
                                self.reset_bus_state(bus)
                    else:
                        assert bus.lane_target == loc, 'must wanna be still'
                        pass

            else: # wish berth is none, overtake-out case
                assert bus.lane_target is not None, 'the bus must have lane target'
                if bus.lane_target > loc:
                    assert bus.lane_target == loc+1, 'target must be neighbor'
                    if bus.react_left_step > 0:
                        bus.react_left_step -= 1
                    else:
                        if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                            self._place_pre_occupies[bus.lane_target] = bus
                            self._place_order_marks[loc+1] = None
                            bus.move_up_step += 1
                        if bus.move_up_step == bus.MOVE_UP_STEPS:
                            self._place_buses_running[loc] = None
                            self._place_pre_occupies[bus.lane_target] = None
                            self._place_buses_running[bus.lane_target] = bus
                            self.reset_bus_state(bus)
                else: # lane_target is self, pass
                    pass

    def _berth_move_up_operation(self, loc):
        bus = self._buses_in_berth[loc]
        if bus is None: return

        # most downstream berth, check if served
        if loc == (self._berth_num-1):
            if bus.is_served:
                self._berth_discharge_to_buffer()
                return
            else:
                # already the most-downstream stop, start to serve!
                self._buses_serving[loc] = bus
                return

        # not the most-downstream berth ...
        if bus.lane_target is None: # check if can move to the next berth
            assert bus.berth_target is not None, 'at least one target'
            if bus.berth_target > loc: # has target
                assert bus.berth_target == loc+1, 'target berth is not near'
                if bus.react_left_step > 0:
                    bus.react_left_step -= 1
                else:
                    if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                        self._pre_occupies[bus.berth_target] = bus
                        self._order_marks[bus.berth_target] = None # already head to it, remove order
                        bus.move_up_step += 1
                    if bus.move_up_step == bus.MOVE_UP_STEPS: # has already reached the next berth
                        self._buses_in_berth[loc] = None
                        self._insertion_marks[loc] = False
                        # if bus.bus_id == 40:
                            # print('~~~', loc, bus.move_up_step, self.current_time)
                        self._pre_occupies[bus.berth_target] = None
                        self._buses_in_berth[bus.berth_target] = bus
                        bus.move_up_step = 0
                        bus.react_left_step = None
                        bus.is_moving_target_set = False
            else:
                assert bus.berth_target == loc, 'must wanna stay in the berth'
                if bus.is_served:
                    pass # record the delay here
                else:
                    self._buses_serving[loc] = bus

        else: # has lane target
            assert bus.lane_target == loc+1, 'if has lane target, must be the next place'
            assert self._queue_rule in ['LO-Out','FO-Bus','FO-Lane'], 'rules that have lane target'
            assert bus.berth_target is None, 'one and only one target'
            assert bus.is_served is True, 'must finish service, otherwise will not set lane as target'

            # check the insertion
            if self._insertion_marks[bus.lane_target] == True:
                assert self._queue_rule in ['FO-Bus','LO-In-Lane','FO-Lane'], 'must be the overtake-in rules'
                # print(bus.bus_id)
                # assert bus.move_up_step == 0, 'the bus should not be in moving'
                # do nothing, just record exit delay
                # if bus.bus_id == 38:
                    # print(bus.move_up_step, self._insertion_marks[bus.lane_target], self.current_time)
            else:
                if bus.react_left_step > 0:
                    self._place_pre_occupies[loc+1] = bus
                    bus.react_left_step -= 1
                else:
                    if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                        self._place_pre_occupies[loc+1] = bus
                        self._place_order_marks[loc+1] = None
                        bus.move_up_step += 1
                        if bus.bus_id == 38:
                            print('berth is moving to lane-', loc+1, 'at step-', bus.move_up_step, self.current_time)
                    if bus.move_up_step == bus.MOVE_UP_STEPS: # already moved to the lane
                        self._buses_in_berth[loc] = None
                        self._place_pre_occupies[bus.lane_target] = None
                        self._place_buses_running[bus.lane_target] = bus
                        bus.move_up_step = 0
                        bus.is_moving_target_set = False
                        


    ########################## target updates ##########################

    def _check_grab_and_set_for_berth(self, which_berth):
        bus = self._buses_in_berth[which_berth]
        if self._order_marks[which_berth+1] == None or self._order_marks[which_berth+1] == bus: # no one order, or ordered by itself, can move to
            bus.berth_target = which_berth+1
            bus.lane_target = None
            self._remove_old_mark(bus)
            self._order_marks[which_berth+1] = bus
            bus.is_moving_target_set = True
            return True

        else: # is already ordered, must be ordered by the bus in the passing lane
            # check if can grab?
            ordered_by_bus = self._order_marks[which_berth+1]
            # 1. find the bus in the passing lane
            order_location = -1
            for index, bus_i in enumerate(self._place_buses_running):
                if bus_i == ordered_by_bus:
                    order_location = index
            # 2. find the bus in the entry queue (in reaction or moving up)
            is_to_grab = False
            if order_location < which_berth-1: # ordered by a far-away bus (must in the passing lane)
                is_to_grab = True
            else:
                if order_location == which_berth-1 and ordered_by_bus.move_up_step == 0:
                # if order_location == which_berth-1 and ordered_by_bus.move_up_step == 0:
                    is_to_grab = True
            if is_to_grab:
                # set itself
                bus.berth_target = which_berth+1
                bus.lane_target = None
                bus.is_moving_target_set = True
                self._remove_old_mark(bus)
                self._order_marks[which_berth+1] = bus

                # set the one being grabbed
                if order_location == -1: # the grabbed bus is in the queue
                    # ordered_by_bus.berth_target = None
                    # ordered_by_bus.lane_target = 0
                    # ordered_by_bus.wish_berth = which_berth
                    # self._remove_old_mark(ordered_by_bus)
                    # self._order_marks[which_berth] = ordered_by_bus
                    # bus.is_moving_target_set = True
                    # bus.react_left_step = 0
                    self.reset_bus_state(ordered_by_bus)
                    self._remove_old_mark(ordered_by_bus)
                else:
                    ordered_by_bus.wish_berth = which_berth
                    ordered_by_bus.is_moving_target_set = False
                    self._remove_old_mark(ordered_by_bus)
                    self._order_marks[which_berth] = ordered_by_bus
                return True

            else: # is ordered and cannot grab, stay still
                bus.berth_target = which_berth
                bus.lane_target = None
                return False
            

    def _set_order_and_target_b2l(self, from_which_berth):
        ### return is a 2-element tuple
        ### the first element is None or from_which_berth+1, 
        ### the second element is the reaction time if any
        # check if the adjacent place has bus
        bus = self._buses_in_berth[from_which_berth]
        bus_adjacent = self._place_buses_running[from_which_berth]
        # cross validation
        if self._pre_occupies[from_which_berth+1] is None \
                and self._place_pre_occupies[from_which_berth+1] is None \
                    and self._order_marks[from_which_berth+1] is None:
        # if bus_adjacent is None or bus_adjacent.move_up_step == 0: # no adjacent bus
            bus_next_place = self._place_buses_running[from_which_berth+1]
            if bus_next_place is None: # no adjacent bus and no bus in the next place
                if bus.bus_id == 2:
                    print(bus_next_place, self.current_time)
                if self._place_order_marks[from_which_berth+1] == None:
                    if self._insertion_marks[from_which_berth+1] == False: # the bus in the next berth is fifo in
                        return (from_which_berth+1, 0)
                # else:
                    # if bus.bus_id == 5:
                        # print(self._place_order_marks[from_which_berth+1].bus_id, self.current_time)
            else: # no adjacent bus, but has bus in the next place
                if bus_next_place.move_up_step > 0: # the bus in the next place is leaving
                    if self._place_order_marks[from_which_berth+1] == None:
                        if self._insertion_marks[from_which_berth+1] == False: # the bus in the next berth is fifo in
                            reaction_time = max(bus.REACT_STEPS - bus_next_place.move_up_step, 0)
                            return (from_which_berth+1, reaction_time)
        else:
            pass
        return (None, None)

    def _check_ot_in_berth_from_queue(self, check_berth, bus):
        bus_in_berth = self._buses_in_berth[check_berth]
        bus_heading_to_berth = self._pre_occupies[check_berth]
        order_by_bus = self._order_marks[check_berth]
        if bus_in_berth == None:
            if bus_heading_to_berth == None and order_by_bus == None:
                return True
            else: # the entry queue has the lowest 'grab' power, no need to check 'grab'
                return False
        else: # the berth is not empty
            # if bus_in_berth.is_moving_target_set == False:
            if bus_in_berth.move_up_step == 0:
                return False
            else:
                if bus_heading_to_berth == None and order_by_bus == None:
                    return True
                else:
                    return False


    def _remove_old_mark(self, bus):
        for index, ordered_bus in enumerate(self._order_marks):
            if ordered_bus == bus:
                self._order_marks[index] = None
                break

    def _update_targets(self, current_time):
        for loc in range(self._berth_num-1,-1,-1):
            ######### update buses in the lane #########
            self._update_lane_target(loc)

            ######### update buses in the berths #########
            self._berth_target_update(loc)

        ######### update buses in the entry queue #########
        self._entry_queue_target_update(current_time)

    def _entry_queue_target_update(self, current_time):
        if self._entry_queue.get_queue_length() == 0: return
        bus = self._entry_queue.get_head_bus(current_time)
        if bus is None: return
        if bus.is_moving_target_set == True: return

        bus_in_upstream_berth = self._buses_in_berth[0]
        if bus_in_upstream_berth is None:
            # no bus can 'jump' out of the entry queue and head to the most-upstream berth
            bus.berth_target = 0
            bus.lane_target = None
            bus.react_left_step = 0
            bus.wish_berth = None
            bus.is_moving_target_set = True
        else:
            if bus_in_upstream_berth.move_up_step > 0: # will move next step
                bus.berth_target = 0
                bus.lane_target = None
                bus.wish_berth = None
                bus.react_left_step = max(bus.REACT_STEPS - bus_in_upstream_berth.move_up_step, 0)
                bus.is_moving_target_set = True
            else: # the bus in the upstream berth will be still
                # check if can overtake into the berth
                if self._queue_rule in ['LO-In-Bus', 'FO-Bus', 'FO-Lane', 'LO-In-Lane']:
                    bus_in_upstream_place = self._place_buses_running[0]
                    if bus_in_upstream_place == None or bus_in_upstream_place.move_up_step > 0:
                        for b in range(self._berth_num-1, 0, -1):
                            can_ot_in = self._check_ot_in_berth_from_queue(b, bus)
                            if can_ot_in == True:
                                bus.berth_target = None
                                bus.lane_target = 0
                                bus.wish_berth = b
                                self._remove_old_mark(bus)
                                self._order_marks[b] = bus
                                bus.is_moving_target_set = True
                                if bus_in_upstream_place == None:
                                    # bus.react_left_step = 0 # ~~~
                                    bus.react_left_step = bus.REACT_STEPS
                                else:
                                    bus.react_left_step = max(bus.REACT_STEPS - bus_in_upstream_place.move_up_step, 0)
                                    # bus.react_left_step = bus.REACT_STEPS ~~~
                                break
                        else: # no berth can be overtoken-in
                            bus.berth_target = None
                            bus.lane_target = None

                    else: # the upstream place is not available
                        bus.berth_target = None
                        bus.lane_target = None
                    
                    
                else: # the rule is not allowed
                    bus.lane_target = None
                    bus.berth_target = None

    def _update_lane_target(self, loc):
        # return ordered berth by the bus in the passing lane
        bus = self._place_buses_running[loc]
        if bus is None: return
        if bus.is_moving_target_set == True: return
        if bus.move_up_step != 0: return # only update the 'exactly' in the berth (or place)
        
        # if bus.bus_id == 3:
        #     print(loc, bus.wish_berth, self.current_time)

        if loc == self._berth_num-1:
            bus.lane_target = 'leaving'
            bus.berth_target = None
            bus.is_moving_target_set = True
            return
        # not the most-downstream space ...
        if bus.is_served: # for overtake-out
            assert self._queue_rule not in ['LO-In-Bus', 'LO-In-Lane'], 'bus in the lane with these rules is not served'
            bus.berth_target = None
            self._check_target_and_set_l2l(loc)

        else: # not served, for overtake-in only
            assert bus.wish_berth is not None, 'wish berth is none, otherwise not be passing lane without being served'
            # update the wish_berth if possible

            assert bus.wish_berth >= loc+1, 'overpass!'
            if bus.wish_berth == loc+1:
                bus_in_next_berth = self._buses_in_berth[loc+1]
                if self._pre_occupies[loc+1] is None:
                    if bus_in_next_berth is None:
                        # cross validation
                        # i.e. check if the some bus is moving from berth towards lane
                        if self._place_pre_occupies[loc+1] is None:
                            self._remove_old_mark(bus)
                            self._order_marks[loc+1] = bus
                            bus.berth_target = loc+1
                            bus.lane_target = None
                            bus.react_left_step = 0
                            bus.is_moving_target_set = True
                        else:
                            bus.lane_target = loc
                            bus.berth_target = None
                    else:
                        if self._place_pre_occupies[loc+1] is None:
                            if bus_in_next_berth.move_up_step > 0:
                                if bus.bus_id == 40:
                                    print(bus.bus_id, 'from lane to occupy time: ', self.current_time)
                                self._remove_old_mark(bus)
                                self._order_marks[loc+1] = bus
                                bus.berth_target = loc+1
                                bus.lane_target = None
                                bus.react_left_step = max(bus.REACT_STEPS - bus_in_next_berth.move_up_step, 0)
                                bus.is_moving_target_set = True
                            else:
                                bus.lane_target = loc
                                bus.berth_target = None
                        else:
                            bus.lane_target = loc
                            bus.berth_target = None

                else: # one bus is heading to it, wait, cannot go further along the passing lane
                    bus.lane_target = loc
                    bus.berth_target = None
            else: # still far-away the wish berth, to see if can go along the lane
                self._check_target_and_set_l2l(loc)
                bus.berth_target = None

    def _berth_target_update(self, which_berth):
        bus = self._buses_in_berth[which_berth]
        if bus == None: return
        if bus.is_moving_target_set == True: return
        if bus.move_up_step != 0: return # only update the 'exactly' in the berth (or place)
        
        if bus.is_served:
            # most-downstream berth ...
            if which_berth == (self._berth_num-1): # most downstream berth, directly leave
                bus.berth_target = 'leaving'
                bus.lane_target = None
                bus.is_moving_target_set = True
                return
            # not the most-downstream berth ...
            bus_running_next_berth = self._buses_in_berth[which_berth+1]

            # first check if can FIFO out
            if bus_running_next_berth == None: # the next berth is empty
                if self._pre_occupies[which_berth+1] is None: # no bus heading to it
                    is_set = self._check_grab_and_set_for_berth(which_berth)
                    bus.react_left_step = 0 # if can move, no need to react
                    if is_set: bus.is_moving_target_set = True
                else: # one bus is heading to it
                    bus.berth_target = which_berth
                    bus.lane_target = None

            else: # the next berth is not empty
                # if bus_running_next_berth.is_moving_target_set == False:
                if bus_running_next_berth.move_up_step == 0: #the next bus in the berth is not moving
                    if self._pre_occupies[which_berth+1] is not None: raise SystemExit('Error: conflict-1')
                    # check the overtake-out rule
                    if self._queue_rule in ['LO-Out', 'FO-Bus', 'FO-Lane']:
                        # check the insertion mark
                        (order_place, return_reaction) = self._set_order_and_target_b2l(which_berth)
                        if order_place is not None:
                            bus.lane_target = order_place
                            bus.berth_target = None
                            bus.react_left_step = return_reaction
                            bus.is_moving_target_set = True
                            self._place_order_marks[order_place] = bus
                        else:
                            bus.berth_target = which_berth
                            bus.lane_target = None
                    else: # cannot overtake-out
                        bus.berth_target = which_berth
                        bus.lane_target = None
                else: # the next bus is moving
                    if self._pre_occupies[which_berth+1] == None: # no bus heading to it
                        is_set = self._check_grab_and_set_for_berth(which_berth)
                        if is_set: 
                            bus.is_moving_target_set = True
                            bus.react_left_step = max(bus.REACT_STEPS - bus_running_next_berth.move_up_step, 0)
                    else: # one bus is heading to it
                        bus.berth_target = which_berth
                        bus.lane_target = None

        else: # the bus is not served
            # most-downstream berth ...
            if which_berth == (self._berth_num-1):
                bus.berth_target = which_berth # stay still and serve
                bus.lane_target = None
                return

            # not the most-downstream berth ...
            # already in the berth, three cases
            # 0. bus is serving
            if bus in self._buses_serving:
                bus.berth_target = which_berth
                bus.lane_target = None
            else:
                # 1. not advanced to the most-downstream vacant berth yet
                # if bus.wish_berth == which_berth:
                #     bus.berth_target = which_berth
                #     bus.lane_target = None
                #     return

                # just check next berth
                bus_running_next_berth = self._buses_in_berth[which_berth+1]

                if bus_running_next_berth is None: # the next berth is empty
                    if self._pre_occupies[which_berth+1] == None: # no bus heading to it
                        is_set = self._check_grab_and_set_for_berth(which_berth)
                        if is_set:
                            bus.is_moving_target_set = True
                            bus.react_left_step = 0

                        # bus.berth_target = which_berth+1
                        # bus.lane_target = None
                        # self._remove_old_mark(bus)
                        # self._order_marks[which_berth+1] = bus
                        # bus.react_left_step = 0
                        # bus.is_moving_target_set = True
                    else: # one bus is heading to it, start to serve~
                        bus.berth_target = which_berth
                        bus.lane_target = None

                else: # the next berth is not empty
                    # if bus_running_next_berth.is_moving_target_set == False:
                    if bus_running_next_berth.move_up_step == 0: # the next bus is still, start to serve~
                        bus.berth_target = which_berth
                        bus.lane_target = None
                    else: # the next bus is moving
                        if self._pre_occupies[which_berth+1] == None: # no bus heading to it
                            is_set = self._check_grab_and_set_for_berth(which_berth)
                            if is_set: 
                                bus.is_moving_target_set = True
                                bus.react_left_step = max(bus.REACT_STEPS - bus_running_next_berth.move_up_step, 0)
                        else: # one bus is heading to the next berth, start to serve~
                            bus.berth_target = which_berth
                            bus.lane_target = None

            # 2. not in the assigned berth, future...

    def _check_target_and_set_l2l(self, loc):
        bus = self._place_buses_running[loc]
        bus_next_place = self._place_buses_running[loc+1]
        if bus_next_place is None:
            # check if any bus in the berth is moving to it
            if self._place_pre_occupies[loc+1] is None: # no bus in the berth is heading to it
                # check if the lane is blocked
                if self._insertion_marks[loc+1] == True and self._queue_rule in ['FO-Lane']: # the lane is blocked 
                    bus.lane_target = loc
                else: # the lane is not blocked
                    bus.lane_target = loc+1
                    bus.react_left_step = 0
                    bus.is_moving_target_set = True
                    self._place_order_marks[loc+1] = bus
            else: # one bus is heading to it
                bus.lane_target = loc
                
        else: # the next place is not empty
            # if bus_next_place.is_moving_target_set == False:
            if bus_next_place.move_up_step == 0:
                bus.lane_target = loc
            else: # the bus in the next place is moving, follow!
                if self._place_pre_occupies[loc+1] is None: # no bus in the berth is heading to it
                    # check if the lane is blocked
                    if self._insertion_marks[loc+1] == True and self._queue_rule in ['FO-Lane']: # the lane is blocked 
                        bus.lane_target = loc
                    else: # the lane is not blocked 
                        bus.react_left_step = max(bus.REACT_STEPS - bus_next_place.move_up_step, 0)
                        bus.lane_target = loc+1
                        bus.is_moving_target_set = True
                        self._place_order_marks[loc+1] = bus
                else: # one bus is heading to it
                    bus.lane_target = loc

