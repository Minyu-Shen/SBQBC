import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import product
from collections import defaultdict


def set_x_y_draw(x_label, y_label):
    # draw settings
    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.grid(linestyle="--")
    ax.tick_params(axis="both", which="major", labelsize=11)

    return plt, ax


def plot_time_space(berth_num, total_buses, duration, sim_delta, stop):
    jam_spacing = 10
    colors = ["r", "g", "b", "y", "k", "w"]
    count = 0
    sorted_list = sorted(total_buses, key=lambda x: x.bus_id, reverse=False)
    # plot the insertion mark
    for berth, times in stop.berth_state.items():
        for i in range(len(times) - 1):
            if times[i] == True or times[i + 1] == True:
                plt.hlines(
                    berth + 1, i * sim_delta, (i + 1) * sim_delta, "r", linewidth=8
                )

    for bus in sorted_list:
        # print(bus.bus_id)
        j = count % 5
        # j = bus.assign_berth
        lists = sorted(
            bus.trajectory_locations.items()
        )  # sorted by key, return a list of tuples
        x, y = zip(*lists)  # unpack a list of pairs into two tuples
        x_list = list(x)
        y_list = list(y)
        for i in range(len(x) - 1):
            y_1 = y_list[i] - 10 if y_list[i] > 8 else y_list[i]
            y_2 = y_list[i + 1] - 10 if y_list[i + 1] > 8 else y_list[i + 1]
            y_tuple = (y_1, y_2)
            x_tuple = (x_list[i], x_list[i + 1])

            if y_list[i + 1] > 8:
                plt.plot(x_tuple, y_tuple, colors[j], linestyle="dotted", linewidth=1)
            else:
                plt.plot(x_tuple, y_tuple, colors[j])
        # plot the service time
        if bus.service_berth is not None:
            plt.hlines(
                (bus.service_berth + 1),
                bus.service_start_mmt,
                bus.service_end_mmt,
                "gray",
                linewidth=5,
            )
        count += 1
    plt.show()


def check_convergence(eval_mean_list, threshold):
    std = np.std(np.array(eval_mean_list))
    return True if std <= threshold else False


def calculate_list_std(data_list):
    mean = sum(data_list) / len(data_list)
    std = math.sqrt(sum([(xi - mean) ** 2 for xi in data_list]) / (len(data_list) - 1))
    return std


def calculate_avg_delay(total_buses):
    # calculate delays
    bus_count = 0
    bus_delay_count = 0.0
    for bus in total_buses:
        if bus.dpt_stop_mmt is not None:  # only count the buses that have left the stop
            bus_delay_count += bus.dpt_stop_mmt - bus.arr_mmt - bus.total_service_time
            # bus_delay_count += bus.enter_delay
            # bus_delay_count += bus.exit_delay
            bus_count += 1
    return bus_delay_count / bus_count * 1.0


# def generate_line_info(
#     line_num,
#     total_arrival,
#     mean_service,
#     arr_scale,
#     service_scale,
#     arrival_cvs=(1.0, 1.0),
#     service_cvs=(0.4, 0.6),
# ):
#     """
#     total_arrival - buses/hr
#     mean_service - seconds
#     """
#     # arrival line infos
#     if line_num == 1:
#         return {0: [total_arrival, arrival_cvs[0]]}, {0: [mean_service, service_cvs[0]]}

#     arr_scale = 5  # larger scale, smaller variance of arrival flow mean
#     arr_flows = (
#         np.random.dirichlet(np.ones(line_num) * arr_scale, size=1).squeeze()
#         * total_arrival
#     )

#     # service line infors
#     service_scale = 20  # larger scale, smaller variance of service mean
#     service_means = (
#         np.random.dirichlet(np.ones(line_num) * service_scale, size=1).squeeze()
#         * mean_service
#         * line_num
#     )
#     flow_infos = {}
#     service_infos = {}

#     for i in range(line_num):
#         arr_cv = (
#             arrival_cvs[0]
#             if arrival_cvs[0] == arrival_cvs[1]
#             else np.random.uniform(arrival_cvs[0], arrival_cvs[1])
#         )
#         flow_infos[i] = (arr_flows[i], arr_cv)
#         service_cv = (
#             service_cvs[0]
#             if service_cvs[0] == service_cvs[1]
#             else np.random.uniform(service_cvs[0], service_cvs[1])
#         )
#         service_infos[i] = (service_means[i], service_cv)

#     return flow_infos, service_infos


def assign_plan_enumerator(line_num, berth_num):
    berths = [i for i in range(berth_num)]
    for roll in product(berths, repeat=line_num):  # roll is a tuple
        if (
            len(set(roll)) == berth_num
        ):  # all berths should be assigned at least one line
            yield {l: roll[l] for l in range(line_num)}


def make_assign_plan(line_num, berth_num, flow_infos, service_infos):
    berths = [i for i in range(berth_num)]
    plans = []
    for roll in product(berths, repeat=line_num):  # roll is a tuple
        if (
            len(set(roll)) == berth_num
        ):  # all berths should be assigned at least one line
            plans.append({l: roll[l] for l in range(line_num)})

    return plans


def calculate_rho(assign_plan, flow_infos, service_infos):
    """
    assign_plan - dictionary: line->berth
    flow_infors - dictionary: line->(arr_mean, arr_cv)
    service_infos - dictionary: line->(serv_mean, serv_cv)
    """
    berth_rho_dict = defaultdict(float)  # berth->rho
    for line, berth in assign_plan.items():
        arr_mean = flow_infos[line][0] / 3600  # buses/hr -> buses/sec
        serv_mean = service_infos[line][0]
        berth_rho_dict[berth] += arr_mean * serv_mean

    return berth_rho_dict


def uniform_sample_from_unit_simplex(size, dim, scale=1.0):
    # sample from dirichlet distribution
    samples = np.random.dirichlet(np.ones(dim) * scale, size=size).squeeze()
    # print(samples.shape)

    # fig, ax = plt.subplots()
    # ax.scatter(samples[:, 0:1], samples[:, 1:2], s=4)
    # fig.savefig("figs/sample_simplex.jpg")

    return samples


if __name__ == "__main__":
    samples = uniform_sample_from_unit_simplex(5000, 3)

    # for i in assign_plan_enumerator(line_num=3, berth_num=2):
    #     print(i)
