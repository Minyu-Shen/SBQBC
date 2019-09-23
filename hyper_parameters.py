# delta_t = 1.0
# sim_duration = 3600  # 100sec
# dspt_headway = 5 * 60  # min * 60
# sim_bus_no = sim_duration//dspt_headway + 1
# dspt_times = [x*dspt_headway for x in range(sim_bus_no)]

# # stops
# stop_num = 12
# stop_spacing = 1000 # inter-stop distance
# stop_locations = [(x+1)*stop_spacing for x in range(stop_num)]
# demand_rates = [7/60.0] * stop_num
# board_rates = [0.5] * stop_num

# # links 
# link_num = stop_num
# link_lengths = [stop_spacing] * link_num
# link_mean_speeds = [20/3.6] * link_num # m/s
# link_cv_speeds = [0.5] * link_num
# link_start_offsets = [x*stop_spacing for x in range(link_num)]

import math

jam_spacing = 12 # meters
move_up_speed = 20 # km/h
back_ward_speed = 80/3 # km/h approximately 27
move_up_time = jam_spacing / (move_up_speed/3.6)
react_time = jam_spacing / (back_ward_speed/3.6)
move_up_time = round(move_up_time, 2)
react_time = round(react_time, 2)
print('move_up_time: {}, and react_time: {}'.format(move_up_time, react_time)) 
# simulation time delta
# calculated by greatest common divisor of move_up_time and react_time
sim_delta = math.gcd(int(move_up_time*100), int(react_time*100)) / 100
print('sim_delta: {}'.format(sim_delta))
reaction_steps = int(react_time/sim_delta)
move_up_steps = int(move_up_time/sim_delta)

print('reaction_steps: {}, move_up_steps: {}'.format(reaction_steps, move_up_steps))