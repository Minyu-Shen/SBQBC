import numpy as np


class DistDwell(object):
    def __init__(self, route_dists):
        self._route_dists = route_dists  # pax/sec
        self._rt_dwell_times = {}
        self._dwell_time_gen()

    def get_random_serv_time(self, rt):
        return self._rt_dwell_times[rt].pop()

    def _dwell_time_gen(self):
        random_time_num = 500000
        for rt, dist in self._route_dists.items():
            mean_serv, cv_serv = dist[0], dist[1]
            if cv_serv == 0:
                serv_time = [mean_serv] * random_time_num
            else:
                shape = 1 / (cv_serv ** 2)
                scale = mean_serv / shape
                serv_time = np.random.gamma(shape, scale, random_time_num).tolist()
                serv_time = [
                    0.55 if x <= 0.54 else x for x in serv_time
                ]  # at least one simulation delta~
            self._rt_dwell_times[rt] = serv_time


if __name__ == "__main__":
    dd = DistDwell({0: [25, 0.1]})
    print(dd.get_random_serv_time(0))
