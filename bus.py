import hyper_parameters as paras
from collections import defaultdict

class Bus(object):
    # board_rate = 0.25 # pax/sec
    SIM_DELTA = paras.sim_delta
    MOVE_UP_STEPS = paras.move_up_steps
    REACT_STEPS = paras.reaction_steps

    def __init__(self, bus_id, route):
        self.bus_id = bus_id
        self.route = route
        
        ### stats, for corridor, it should be changed to a list, future work ...
        self.arr_mmt = None # the time when a bus arrives in the entry queue
        self.dpt_stop_mmt = None # the time when a bus leaves stop
        self.service_start_mmt = None # the time when a bus enters the berth to serve
        self.service_end_mmt = None # the time when a bus finishes service
        self.enter_delay = 0.0
        self.exit_delay = 0.0

        self.arr_time = -1.0 # arrived time at stops, negative means not arrived; 
        self.etr_time = -1.0
        self.dpt_time = -1.0
        self.serv_time = -1.0
        
        # 'leaving', '1', '2', ... target berth
        self.berth_target = None
        self.lane_target = None
        self.is_served = False
        self.wish_berth = None
        self.is_moving_target_set = False

        ### traffic characteristics in stop
        self.move_up_step = 0
        self.reaction_step = None
        self.react_left_step = None

        ### trajectory
        self.trajectory = []
        self.trajectory_times = []
        self.lane_trajectory = []
        self.lane_trajectory_times = []
        self.trajectory_locations = defaultdict(float)
        
        self.service_berth = None
    # def record_trajectory(self, curr_t):
    #     pass
