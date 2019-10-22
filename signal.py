class Signal(object):
    def __init__(self, cycle_length, green_ratio, buffer_size=1000):
        self._cycle_length = cycle_length
        self._green_ratio = green_ratio
        # self._buffer_size = buffer_size # default is infinite; i.e. no impact on the stop
        # self._queue = []

    def is_green(self, curr_t):
        if (curr_t % self._cycle_length) < self._cycle_length*self._green_ratio:
            return True
        else:
            return False

    # def get_buffer_size(self):
    #     return self._buffer_size

    # def enter_bus(self, bus):
    #     self._queue.append(bus)

    # def is_queue_full(self):
    #     if len(self._queue) < self._buffer_size:
    #         return False
    #     else:
    #         return True
    
    # def discharge(self, curr_t):
    #     if self.is_green(curr_t):
    #         self._queue = []

class Buffer(object):
    def __init__(self, buffer_size, down_signal):
        self.buffer_size = buffer_size
        self._buses_in_buffer= [None] * buffer_size # 0 is the most downstream
        self.last_ordered = False
        self.down_signal = down_signal

    def update_time_space_info(self, current_time, berth_num):
        for buffer_id in range(self.buffer_size):
            bus = self._buses_in_buffer[buffer_id]
            if bus is None: continue
            bus.trajectory_locations[current_time] = berth_num + buffer_id + 1

    def check_last_buffer(self):
        if self._buses_in_buffer[0] is None:
            return (self.last_ordered, None)
        else:
            return (self.last_ordered, self._buses_in_buffer[0].move_up_step)

    def set_occupation(self, bus):
        bus.move_up_step = 0
        bus.is_moving_target_set = False
        self._buses_in_buffer[0] = bus
        self.last_ordered = False

    def discharge(self, curr_t):
        if self.buffer_size > 0:
            for loc in range(self.buffer_size-1,-1,-1):
                self._set_target(loc, curr_t)
                self._move_up_operation(loc, curr_t)

    def _move_up_operation(self, loc, curr_t):
        # for loc in range(self.buffer_size-1,-1,-1):
        bus = self._buses_in_buffer[loc]
        if bus is None: return
        if bus.is_moving_target_set == False: return

        if bus.react_left_step > 0:
            bus.react_left_step -= 1
        else:
            bus.move_up_step += 1
            if bus.move_up_step == bus.MOVE_UP_STEPS:
                self.forward(loc)

    def _set_target(self, loc, curr_t):
        # for loc in range(self.buffer_size-1,-1,-1):
        bus = self._buses_in_buffer[loc]
        if bus is None: return
        if bus.is_moving_target_set == True: return
        
        if loc == self.buffer_size-1:
            if self.down_signal.is_green(curr_t):
                bus.react_left_step = 0
                bus.is_moving_target_set = True
        else:
            next_bus = self._buses_in_buffer[loc+1]
            if next_bus is None or next_bus.move_up_step > 0:
                bus.is_moving_target_set = True
                if next_bus is not None:
                    bus.react_left_step = max(bus.REACT_STEPS - next_bus.move_up_step, 0)
                else:
                    bus.react_left_step = 0

    def forward(self, loc):
        if loc == self.buffer_size-1:
            self._buses_in_buffer[loc] = None
        else:
            self._buses_in_buffer[loc+1] = self._buses_in_buffer[loc]
            self._buses_in_buffer[loc+1].is_moving_target_set = False
            self._buses_in_buffer[loc+1].move_up_step = 0
            self._buses_in_buffer[loc] = None
        

