from bus import Bus
import numpy as np
import math
import random
from dist_stop import DistStop

np.random.seed(13)
random.seed(1) # 15

class Generator(object):
    total_bus = 0
    def __init__(self, flows, duration, assign_plan=None):
        self._flows = flows
        self._schedules = {}
        self._init_schedule(duration)
        self._assign_plan = assign_plan

    def _init_schedule(self, duration):
        for rt, flow in self._flows.items():
            mean_hdw = 3600.0 / flow[0] # in seconds
            cv_hdw = flow[1]
            arr_times = self._gamma_arrive(duration, mean_hdw, cv_hdw)
            self._schedules[rt] = arr_times
    
    def poisson_generator(self, rate, t_start, t_stop):
        sts = []
        lasttime = 0
        while lasttime <= (t_stop):
            next_st = -math.log(1.0 - random.random()) / rate
            lasttime += next_st
            sts.append(lasttime)
        return sts

    def _gamma_arrive(self, duration, mean_hdw, cv_hdw):
        shape = 1 / (cv_hdw**2)
        scale = mean_hdw / shape
        arr_times = list()
        tests = []
        if cv_hdw == 1.0: # poisson case
            return self.poisson_generator(1/mean_hdw, t_start=0, t_stop=duration)
        else:
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
        
        mean = np.mean(np.array(tests))
        standard = np.std(np.array(tests))
        print(mean, standard)
        return arr_times
    
    def dispatch(self, t, persistent=False):
        if not persistent:
            dspting_buses = []
            for rt, schedule in self._schedules.items():
                while schedule[0] <= t:
                    schedule.pop(0)
                    if self._assign_plan is None:
                        bus = Bus(Generator.total_bus, rt, berth=None)
                    else:
                        bus = Bus(Generator.total_bus, rt, berth=self._assign_plan[rt])
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
            if self._assign_plan is None:
                bus = Bus(Generator.total_bus, route=0, berth=None)
            else:
                rt = random.randint(0,3)
                bus = Bus(Generator.total_bus, route=rt, berth=self._assign_plan[rt])
                        
            Generator.total_bus += 1
            return bus

if __name__ == "__main__":
    import hyper_parameters as paras
    
    flows = {0: [50, 1.0], 1:[100, 1.0], 2:[25, 1.0]} # [buses/hr, c.v.]
    assign_plan = {0:1, 1:2, 2:0} # line -> berth
    generator = Generator(flows, 800, assign_plan=assign_plan)

    for t in np.arange(0.0, 800.0, paras.sim_delta):
        buses = generator.dispatch(t)
        # for bus in buses:
            # print(t, 'bus id: ' + str(bus.bus_id), 'bus line: ', str(bus.route))

    # print(generator.poisson_generator(1))
