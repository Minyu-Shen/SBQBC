import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import product, repeat
from collections import defaultdict
import ast
from pymongo import MongoClient
from sacred_to_df import sacred_to_df
import random


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


def assign_plan_enumerator(line_num, berth_num):
    berths = [i for i in range(berth_num)]
    for roll in product(berths, repeat=line_num):  # roll is a tuple
        if (
            len(set(roll)) == berth_num
        ):  # all berths should be assigned at least one line
            yield {l: roll[l] for l in range(line_num)}


def random_assign_plan_enumerator(line_num, berth_num, sample_num=2000):
    berths = [i for i in range(berth_num)]
    for roll in range(sample_num):
        yield {l: random.choice(berths) for l in range(line_num)}


def make_assign_plan(line_num, berth_num, flow_infos, service_infos):
    berths = [i for i in range(berth_num)]
    plans = []
    for roll in product(berths, repeat=line_num):  # roll is a tuple
        if (
            len(set(roll)) == berth_num
        ):  # all berths should be assigned at least one line
            plans.append({l: roll[l] for l in range(line_num)})

    return plans


# def calculate_rho(assign_plan, flow_infos, service_infos):
#     """
#     assign_plan - dictionary: line->berth
#     flow_infors - dictionary: line->(arr_mean, arr_cv)
#     service_infos - dictionary: line->(serv_mean, serv_cv)
#     """
#     berth_rho_dict = defaultdict(float)  # berth->rho
#     for line, berth in assign_plan.items():
#         arr_mean = flow_infos[line][0] / 3600  # buses/hr -> buses/sec
#         serv_mean = service_infos[line][0]
#         berth_rho_dict[berth] += arr_mean * serv_mean

#     return berth_rho_dict


def cal_berth_f_rho_for_each_plan(assign_plan, line_flow, line_service):
    # if assign_plan is a string, covnert it
    """
    line_flow, dict: ln -> info tuple
    line_service, dict: ln -> info tuple
    """
    assign_plan = (
        ast.literal_eval(assign_plan) if type(assign_plan) == str else assign_plan
    )
    line_rho = {
        int(ln): (line_flow[ln][0] / 3600.0) * line_service[ln][0] for ln in line_flow
    }
    berth_num = len(set(assign_plan.values()))
    berth_rho = [0.0] * berth_num
    berth_flow = [0.0] * berth_num
    # berth_flow = [0.0] * berth_num
    # berth_service = [0.0] * berth_num
    for ln, berth in assign_plan.items():
        # berth_service[berth] += line_service[str(ln)][0]
        berth_flow[berth] += line_flow[ln][0]
        berth_rho[berth] += line_rho[ln]
    # berth_rho = [(x / 3600.0) * y for x, y in zip(berth_flow, berth_service)]
    return berth_flow, berth_rho


def uniform_sample_from_unit_simplex(size, dim, scale=1.0):
    # sample from dirichlet distribution
    samples = np.random.dirichlet(np.ones(dim) * scale, size=size).squeeze()
    # print(samples.shape)

    # fig, ax = plt.subplots()
    # ax.scatter(samples[:, 0:1], samples[:, 1:2], s=4)
    # fig.savefig("figs/sample_simplex.jpg")

    return samples


def get_run_df_from_db(stop_setting):
    (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    ) = stop_setting
    client = MongoClient("localhost", 27017)
    db = client["stop"]

    query = "queue_rule==@queue_rule and berth_num=={} and line_num=={} and total_flow=={} and arrival_type==@arrival_type and mean_service=={} and set_no=={}".format(
        berth_num, line_num, total_flow, mean_service, set_no
    )

    # arrival_type = "Gaussian"
    # query = "arrival_type == @arrival_type"
    run_df = sacred_to_df(db.runs).query(query)

    return run_df


def get_run_df_from_near_stop_db(stop_setting, signal_setting):
    (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    ) = stop_setting
    cycle_length, green_ratio, buffer_size = signal_setting
    client = MongoClient("localhost", 27017)
    db = client["near_stop"]

    query = "queue_rule==@queue_rule and berth_num=={} and line_num=={} and total_flow=={} and arrival_type==@arrival_type and mean_service=={} and set_no=={} and cycle_length=={} and green_ratio=={} and buffer_size=={}".format(
        berth_num,
        line_num,
        total_flow,
        mean_service,
        set_no,
        cycle_length,
        green_ratio,
        buffer_size,
    )
    run_df = sacred_to_df(db.runs).query(query)

    return run_df


def get_case_df_from_db(stop_setting, signal_setting, algorithm):
    client = MongoClient("localhost", 27017)
    db = client["case"]

    (
        queue_rule,
        berth_num,
        line_num,
        total_flow,
        arrival_type,
        mean_service,
        set_no,
    ) = stop_setting

    if signal_setting is None:
        query = "algorithm==@algorithm and queue_rule==@queue_rule and berth_num=={} and line_num=={} and total_flow=={} and arrival_type==@arrival_type and mean_service=={} and set_no=={}".format(
            berth_num, line_num, total_flow, mean_service, set_no,
        )
    else:
        cycle_length, green_ratio, buffer_size = signal_setting
        query = "algorithm==@algorithm and queue_rule==@queue_rule and berth_num=={} and line_num=={} and total_flow=={} and arrival_type==@arrival_type and mean_service=={} and set_no=={} and cycle_length=={} and green_ratio=={} and buffer_size=={}".format(
            berth_num,
            line_num,
            total_flow,
            mean_service,
            set_no,
            cycle_length,
            green_ratio,
            buffer_size,
        )

    if algorithm == "CNP":
        appended_query_str = "and max_depth=={} and sample_num_of_each_region=={}".format(
            4, 10
        )
        query = query + appended_query_str

    case_df = sacred_to_df(db.runs).query(query)

    return case_df


if __name__ == "__main__":
    # samples = uniform_sample_from_unit_simplex(5000, 3)
    a = random_assign_plan_enumerator(16, 4, 2)
    for i in a:
        print(i)

    # b = random_combination(a, 2)
    # print(b)

    # for i in assign_plan_enumerator(line_num=3, berth_num=2):
    #     print(i)
