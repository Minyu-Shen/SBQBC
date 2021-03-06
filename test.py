from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy.linalg as LA
import numpy as np
from scipy.optimize import linprog

vertexs = [
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.3333333333333333, 0.3333333333333333, 0.3333333333333333),
]
# vertexs = [
#     (1.0, 0.0, 0.0),
#     (0.3333333333333333, 0.3333333333333333, 0.3333333333333333),
#     (0.0, 0.0, 1.0),
# ]

vertexs = [
    (0.3333333333333333, 0.3333333333333333, 0.3333333333333333),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
]

# vertexs = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

A_list = [list(v) for v in vertexs]
# A_list.append([1.0, 1.0, 1.0])
A = np.array(A_list).T

# b = np.array([0.1, 0.4, 0.5, 1.0])
b = np.array([0.5, 0.4, 0.1])
x = LA.solve(A, b)

# x = linprog(c=[0.0, 0.0, 0.0], A_eq=A, b_eq=b, bounds=(0, None),)

print(x, type(x), np.sum(x) == 1.0)

# point = Point(1 / 3.0, 1 / 3.0, 1 / 3.0)
# polygon = Polygon([[1, 0, 0], [0, 1, 0], [ 0, 0, 1 ]])
# print(polygon.is_valid)
# print(polygon.area)

# print(polygon.contains(point))

# def change(a):
#     a.property = a.property + 55


# class A(object):
#     def __init__(self, property):
#         self.property = property
#         self.mylist = [1,2,3]

#     def get_something(self):
#         one = self.mylist[0]
#         self.mylist[0] = None
#         return '1', one

# def test_method(to_be_modified):
#     to_be_modified.property = 100

# if __name__ == "__main__":

#     a = A(10)
#     print(a.property)
#     test_method(a)
#     print(a.property)


# a = []
# a.append(A(5))
# a.append(A(10))
# s = a[0]
# s.property = 100000
# print(a[0].property )

# a = A(10)
# b = A(20)
# list1 = [a, b]
# list2 = [a, b]
# list1[0].property = 50
# print(list2[0].property)
# print(list1[0].property)
# list2[0].property = 1000
# print(list1[0].property)


# -1.0
# mylist = [A(10),A(20),A(30)]
# a = mylist[0]
# print(id(a))
# mylist[0] = None
# print(id(a))
# print(a.property)

# 0.
# a = A(20)
# print(a.get_something())

# 1.
# a = A(10)
# change(a)
# print(a.property)

# 2.
# import math
# duration = 3600 * 50
# jam_spacing = 12 # meters
# move_up_speed = 22 # km/h
# back_ward_speed = 27 # km/h
# move_up_time = jam_spacing / (move_up_speed/3.6)
# react_time = jam_spacing / (back_ward_speed/3.6)
# print(move_up_time, react_time)

# move_up_time = round(move_up_time, 1)
# react_time = round(react_time, 1)
# print('move_up_time: {}, and react_time: {}'.format(move_up_time, react_time))

# sim_delta = math.gcd(int(move_up_time*10), int(react_time*10)) / 10
# print('sim_delta: {}'.format(sim_delta))

# sim_steps = int(duration / sim_delta)

# print(duration / sim_delta)

