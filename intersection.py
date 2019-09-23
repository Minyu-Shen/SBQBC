class Signal(object):
    def __init__(self, cycle_length, green_ratio, buffer_size=1000):
        self._cycle_length = cycle_length
        self._green_ratio = green_ratio
        self._buffer_size = buffer_size # default is infinite; i.e. no impact on the stop
        self._queue = []

    def is_green(self, curr_t):
        if (curr_t % self._cycle_length) < self._cycle_length*self._green_ratio:
            return True
        else:
            return False
    
    def get_buffer_size(self):
        return self._buffer_size

    def enter_bus(self, bus):
        self._queue.append(bus)

    def is_queue_full(self):
        if len(self._queue) < self._buffer_size:
            return False
        else:
            return True
    
    def discharge(self, curr_t):
        if self.is_green(curr_t):
            self._queue = []
        