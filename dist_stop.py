from stop import Stop
from dist_dwell import DistDwell

# 'process' for methods for sub-stop
# 'operation' for methods in parent-stop
class DistStop(Stop, DistDwell):
    def __init__(self, stop_id, berth_num, queue_rule, route_dists, down_signal=None):
        Stop.__init__(self, stop_id, berth_num, queue_rule, down_signal=down_signal)
        DistDwell.__init__(self, route_dists)

    # 0. inheriting bus_arrival and override, called from outside
    def bus_arrival(self, bus, t):
        Stop.bus_arrival(self, bus, t)
        # generate service time upon arrival in the entry queue
        bus.serv_time = self.get_random_serv_time(bus.route) # inherited from 'DistDwell'

    def _service_process(self, t):
        # update service time for each bus
        for berth_index, bus in enumerate(self._buses_serving):
            if bus == None: continue
            if bus.serv_time > 0:
                if bus.service_start == None:
                    bus.service_start = t
                bus.serv_time -= bus.SIM_DELTA 
                if bus.serv_time <= 0.0:
                    if bus.service_end == None:
                        bus.service_end = t
                    if bus.service_berth == None:
                        bus.service_berth = berth_index
                    bus.is_served = True
                    

    def process(self, t):
        self.current_time = t
        self.update_time_space(t)
        # print('~~~', self._place_pre_occupies[2], self.current_time)
        # if self._order_marks[1] is not None:
            # print(self._order_marks[1].bus_id)

        # b = self._buses_in_berth[1] 
        # if b is not None:
            # print(b.bus_id)

        # assert self._place_buses_running[0] == None, 'test'
        ### 0. update the target berth and target place
        self._update_targets(t)

        # check lane and berth, alternately
        # from downstream to upstream
        for loc in range(self._berth_num-1,-1,-1):
            ### 1. for passing lane
            self._lane_operation(loc)
            
            ### 2. stop (berths) move-up operations
            # if self._berth_moveup_operation(loc) == 'no_service_operation': continue
            self._berth_move_up_operation(loc)

        ### 3. stop (berths) service operations
        self._service_process(t)
    
        self._entry_queue_operation(t)

        # for bbb in self._buses_in_berth:
        #     if bbb is not None and bbb.bus_id == 15:
        #         print(bbb.wish_berth, t)
        # for bbb in self._place_buses_running:
        #     if bbb is not None and bbb.bus_id == 15:
        #         print(bbb.wish_berth, t)

        # for bbb in self._buses_serving:
        #     if bbb is not None and bbb.bus_id == 15:
        #         print(bbb.wish_berth, t)

        # if self._buses_in_berth[2] is not None:
        #     print('~~~~~', self.current_time, self._buses_in_berth[2].bus_id)
        # else:
        #     print('~~~~~~', self.current_time, 'None')