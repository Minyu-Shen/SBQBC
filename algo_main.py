from algo_experiment import algo_ex


@algo_ex.config
def config():
    seed = 0
    berth_num = 2
    line_num = 10
    total_flow = 135  # buses/hr
    arrival_type = "Gaussian"
    mean_service = 25  # seconds

    # signal
    # signal_paras = None
    # signal_paras = {"cycle_length": 120, "green_ratio": 0.5, "buffer_size": 3}

    # cycle_length = None
    # green_ratio = None
    # buffer_size = None

    cycle_length = 120
    green_ratio = 0.5
    buffer_size = 3

    # algorithm
    # algorithm = "Tan"
    algorithm = "CNP"

    ### the following two is dynamically changing
    queue_rule = None
    set_no = None


# for set_no in [1]:
for set_no in [0, 1]:
    for queue_rule in ["FIFO", "LO-Out", "FO-Bus"]:
        algo_ex.run(config_updates={"set_no": set_no, "queue_rule": queue_rule})
