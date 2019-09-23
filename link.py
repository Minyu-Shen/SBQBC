import numpy as np


class Link:
    def __init__(self, link_id, mean_speed, cv_speed, length, start_offset):
        """Init method.

        init method for Link 

        Args:
        length: the total length of this link.
        start_offset: starting offset.

        Returns:
            
        """

        # unchangable ...
        self._link_id = link_id
        self._mean_speed = mean_speed
        self._cv_speed = cv_speed
        self._start_offset = start_offset
        self._length = length
        self._end_offset = start_offset + length
        self._next_stop = None
        
        # changable ...
        self.bus_list = []

    def __call__(self, stop):
        self._next_stop = stop

    def enter_bus(self, bus):
        bus.offset = self._start_offset
        self.bus_list.append(bus)

    def forward(self, delta_t, curr_time):
        speed = np.random.normal(self._mean_speed, self._cv_speed*self._mean_speed, len(self.bus_list))
        # update offset
        for index, bus in enumerate(self.bus_list):
            bus.offset += speed[index] * delta_t
            # update the plotted trajectories
            bus.trajectories[curr_time] = bus.offset
        kept_buses = [bus for bus in self.bus_list if bus.offset < self._end_offset]
        # buses that will leave the link and enter the stop
        sent_buses = [bus for bus in self.bus_list if bus.offset >= self._end_offset]
        for bus in sent_buses:
            self._next_stop.enter_bus(bus, curr_time)
        self.bus_list = kept_buses
        
        return sent_buses
        # if sent_buses:
        #     return {self._next_stop.stop_id: sent_buses}
        # else:
        #     return {}
        
    def reset(self):
        self.bus_list = []

