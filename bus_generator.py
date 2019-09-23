from bus import Bus
import numpy as np
# from normal_pax_stop import NormalPaxStop
from dist_stop import DistStop

np.random.seed(13)

class Generator(object):
    total_bus = 0
    def __init__(self, flows, duration):
        self._flows = flows
        self._schedules = {}
        self._init_schedule(duration)

    def _init_schedule(self, duration):
        for rt, flow in self._flows.items():
            mean_hdw = 3600.0 / flow[0] # in seconds
            cv_hdw = flow[1]
            arr_times = self._inter_gamma(duration, mean_hdw, cv_hdw)
            self._schedules[rt] = arr_times
            
    def _inter_gamma(self, duration, mean_hdw, cv_hdw):
        shape = 1 / (cv_hdw**2)
        scale = mean_hdw / shape
        arr_times = list()
        tests = []
        while True:
            inter_time = np.asscalar(np.random.gamma(shape, scale, 1))
            tests.append(inter_time)
            if len(arr_times) == 0:
                arr_times.append(inter_time)
            else:
                if arr_times[-1] >= duration:
                    break
                else:
                    arr_times.append(arr_times[-1] + inter_time)
        
        # mean = np.mean(np.array(tests))
        # standard = np.std(np.array(tests))
        # print(mean, standard)
        return arr_times
    
    def dispatch(self, t, persistent=False):
        if not persistent:
            dspting_buses = []
            for rt, schedule in self._schedules.items():
                while schedule[0] <= t:
                    schedule.pop(0)
                    bus = Bus(Generator.total_bus, rt)
                    Generator.total_bus += 1
                    dspting_buses.append(bus)
                    # always has a bus's arrival time greater than simulation duration, no need to break
                    # if len(schedule) == 0:
                        # break
            return dspting_buses
        else:
            # dispatch one bus to the stop, if there is no entry queue there
            # persistent case means single-stop capacity scenario, route always = 0
            bus = Bus(Generator.total_bus, route=0)
            Generator.total_bus += 1
            return bus

if __name__ == "__main__":
    import parameters as paras
    
    flows = {0: [50, 0.4]} # buses/hr
    generator = Generator(flows, 800)

    total_convoys = []

    for t in np.arange(0.0, 800.0, paras.sim_delta):
        buses = generator.dispatch(t)
        for bus in buses:
            print('bus id: ' + str(bus.bus_id))
            