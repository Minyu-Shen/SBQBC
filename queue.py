import hyper_parameters as paras

class WaveQueue(object):
    # board_rate = 0.25 # pax/sec
    SIM_DELTA = paras.sim_delta
    MOVE_UP_STEPS = paras.move_up_steps
    REACT_STEPS = paras.reaction_steps

    def __init__(self):
        self._buses = []
        self._last_pop_time = 0

    def pop_one_bus(self, curr_t):
        self._last_pop_time = curr_t - (WaveQueue.MOVE_UP_STEPS * WaveQueue.SIM_DELTA)
        return self._buses.pop(0)

    def enter_one_bus(self, bus):
        self._buses.append(bus)

    def get_queue_length(self):
        return len(self._buses)
    
    def get_head_bus(self, curr_t):
        if curr_t - self._last_pop_time >= (WaveQueue.MOVE_UP_STEPS+WaveQueue.REACT_STEPS) * WaveQueue.SIM_DELTA:
            
            return self._buses[0]

    def advance_one_time_step(self):
        pass