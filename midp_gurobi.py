import numpy as np
from line_profile import get_generated_line_info

berth_num = 2
line_num = 6
line_flow, line_service = get_generated_line_info(
    berth_num, line_num, 135, "Gaussian", 25, 0
)
line_rho = {ln: line_flow[ln][0] / 3600.0 * line_service[ln][0] for ln in line_flow}
total_rho = sum(line_rho.values())


# x = cp.Variable((line_num * berth_num, 1), boolean=True)
# constrs = []
# for ln in range(line_num):
#     # print(ln * berth_num, (ln + 1) * berth_num)
#     constrs.append(cp.sum(x[ln * berth_num : (ln + 1) * berth_num]) == 1)
# print(len(constrs))

# A = np.zeros((berth_num, berth_num * line_num))
# for berth in range(berth_num):
#     for ln_idx in range(line_num):
#         A[berth, berth + ln_idx * berth_num] = line_rho[ln_idx]
# # print(A)

# b = np.array([total_rho] * berth_num) / berth_num
# b = b.reshape(-1, 1)
# # print(b)

# # x = np.array([1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0]).reshape(-1, 1)
# # print(A @ x)

# objective = cp.Minimize(cp.sum_squares(A @ x - b))

# prob = cp.Problem(objective, constrs)
# prob.solve(cp.GLPK_MI)

