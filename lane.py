import hyper_parameters as paras

### check the head of bus, as the position
class Lane(object):
    # SIM_DELTA = paras.sim_delta
    # REACT_TIME = paras.react_time
    # MOVE_UP_TIME = paras.move_up_time
    # MOVE_UP_STEPS = paras.move_up_steps
    # REACT_STEPS = paras.reaction_steps

    def __init__(self, space_num, down_signal=None):
        self._space_size = space_num
        self._down_signal = down_signal
        self._buses = [None] * space_num

        self.place_buses_running = [None] * space_num # moving buses that are not fully occupying the whole place
        self._place_order_marks = [None] * space_num
        self.place_pre_occupies = [None] * space_num # the head running in the berth


    def set_order_and_target_b2l(self, from_which_berth):
        # check if the adjacent place has bus
        bus_adjacent = self.place_buses_running[from_which_berth]
        if bus_adjacent is None: # no adjacent bus
            bus_next_place = self.place_buses_running[from_which_berth+1]
            if bus_next_place is None: # no adjacent bus and no bus in the next place
                self._place_order_marks[from_which_berth+1] = from_which_berth
                return from_which_berth+1
            else: # no adjacent bus, but has bus in the next place
                if bus_next_place.move_up_step > 0:
                    return from_which_berth+1
        
        return None


    def update_lane_target(self, loc, buses_moving_in_berths, order_marks):
        # return ordered berth by the bus in the passing lane
        bus = self.place_buses_running[loc]
        if bus is None: return
        if bus.move_up_step != 0: return # only update the 'exactly' in the berth (or place)

        if loc == self._space_size-1:
            bus.lane_target = 'leaving'
            bus.berth_target = None
            return
        # not the most-downstream space
        if bus.is_served: # for overtake-out
            bus.berth_target = None
            bus_next_place = self.place_buses_running[loc+1]
            if bus_next_place is None:
                # check if any bus in the berth is moving to it
                if self.place_pre_occupies[loc+1] is None: # no bus in the berth is heading to it
                    bus.lane_target = loc+1
                else:
                    bus.lane_target = loc
            else: # the next place is not empty
                if bus_next_place.move_up_step == 0:
                    bus.lane_target = loc
                else: # the bus in the next place is moving, follow!
                    bus.lane_target = loc+1

        else: # not served, for overtake-in only
            # the berth target is already set once she leaves the entry queue
            bus.lane_target = None
            # the berth_target must be set
            if bus.berth_target == None or > bus.berth_target <= loc: # she will not reach the target berth's adjacent place
                raise SystemExit('Conflict-lane-1')


    def place_moveup_operation(loc):
        bus = self.place_buses_running[loc]
        if bus is None: return
        
        if loc == self._space_size-1:
            if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                bus.move_up_step += 1
            else:
                # for now, just leave, in future, add signal
                assert(self._down_signal == None)
                self.place_buses_running[loc] = None

        else:
            # not the most-downstream space
            if bus.berth_target is not None:
                assert(bus.lane_target == None, 'only one target')
                assert(bus.berth_target > loc, 'target berth must be greater than current location')
                if bus.berth_target == loc+1:
                    if 0 <= bus.move_up_step < bus.MOVE_UP_STEPS:
                        
                        self._pre_occupies[bus.berth_target] = bus
                        bus.move_up_step += 1
                    else: # has already reached the next berth
                        self._buses_in_berth[loc] = None
                        self._pre_occupies[bus.berth_target] = None
                        self._buses_in_berth[bus.berth_target] = bus
                        bus.move_up_step = 0

                elif bus.berth_target > loc+1:

                else:
                    assert(bus.berth_target == loc, 'must wanna be still')

            else:
                assert(bus.lane_target is not None, 'targets cannot be all none')
                bus.lane_target
        
       