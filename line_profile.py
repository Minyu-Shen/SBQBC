import json
from os import read
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pickle
from pymongo import MongoClient


def generate_line_info(
    line_num,
    total_arrival,
    arrival_type,
    mean_service,
    arr_scale,
    service_scale,
    arrival_cvs=(1.0, 1.0),
    service_cvs=(0.4, 0.8),
):
    """
    total_arrival - buses/hr
    mean_service - seconds
    arr_scale - # larger scale, smaller variance of arrival flow mean
    service_scale - # larger scale, smaller variance of service time mean
    """
    # arrival line infos
    if line_num == 1:
        return {0: [total_arrival, arrival_cvs[0]]}, {0: [mean_service, service_cvs[0]]}

    arr_flows = (
        np.random.dirichlet(np.ones(line_num) * arr_scale, size=1).squeeze()
        * total_arrival
    )

    # service line infors
    service_means = (
        np.random.dirichlet(np.ones(line_num) * service_scale, size=1).squeeze()
        * mean_service
        * line_num
    )
    flow_infos = {}
    service_infos = {}

    for i in range(line_num):
        arr_cv = (
            arrival_cvs[0]
            if arrival_cvs[0] == arrival_cvs[1]
            else np.random.uniform(arrival_cvs[0], arrival_cvs[1])
        )
        flow_infos[str(i)] = (arr_flows[i], arr_cv, arrival_type)
        service_cv = (
            service_cvs[0]
            if service_cvs[0] == service_cvs[1]
            else np.random.uniform(service_cvs[0], service_cvs[1])
        )
        service_infos[str(i)] = (service_means[i], service_cv)

    return flow_infos, service_infos


def get_generated_line_info(
    berth_num, line_num, total_flow, arrival_type, mean_service, set_no=0
):
    client = MongoClient("localhost", 27017)
    db = client["inputs"]
    collection = db["line_profile"]
    query_dict = {
        "berth_num": berth_num,
        "line_num": line_num,
        "total_flow": total_flow,
        "arrival_type": arrival_type,
        "mean_service": mean_service,
        "set_no": set_no,
    }
    results = collection.find(query_dict)[0]
    # convert the string of line to int, (because MongoDB only support str as key)
    line_flow = {int(ln): flow for ln, flow in results["line_flow"].items()}
    line_service = {int(ln): service for ln, service in results["line_service"].items()}
    line_rho = {
        ln: (line_flow[ln][0] / 3600.0) * line_service[ln][0] for ln in line_flow
    }
    return line_flow, line_service, line_rho


def generate_and_add_to_db():
    client = MongoClient("localhost", 27017)
    db = client["inputs"]
    collection = db["line_profile"]

    berth_num = 2
    line_num = 10
    total_flow = 135
    arrival_type = "Gaussian"
    mean_service = 25
    arr_scale = 4  # larger scale, smaller variance of arrival flow mean
    service_scale = 4  # larger scale, smaller variance of service mean

    for set_no in range(1):
        line_flow, line_service = generate_line_info(
            line_num,
            total_flow,
            arrival_type,
            mean_service,
            arr_scale,
            service_scale,
            arrival_cvs=(0.4, 0.8),
            service_cvs=(0.4, 0.8),
        )
        json_dict = {}
        json_dict["berth_num"] = berth_num
        json_dict["line_num"] = line_num
        json_dict["set_no"] = set_no + 2
        json_dict["total_flow"] = total_flow
        json_dict["arrival_type"] = arrival_type
        json_dict["mean_service"] = mean_service
        json_dict["line_flow"] = line_flow
        json_dict["line_service"] = line_service

        collection.insert_one(json_dict)

        # bar plots
        arrival_flow_list = []
        service_list = []
        for ln, flow in line_flow.items():
            arrival_flow_list.append(flow[0])
            service_list.append(line_service[ln][0])

        # print(service_list)
        x = np.arange(len(line_flow))
        width = 0.25
        fig, ax = plt.subplots()
        flow_bar = ax.bar(
            x - 0.5 * width,
            arrival_flow_list,
            width,
            label="arrival bus flow (buses/hr)",
        )
        # ax2 = ax.twinx()
        service_bar = ax.bar(
            x + 0.5 * width,
            service_list,
            width,
            color="r",
            label="mean service time (seconds)",
        )
        ax.legend()
        # ax2.legend()
        fig.savefig("figs/line_info.jpg")
        # plt.show()


if __name__ == "__main__":
    generate_and_add_to_db()
