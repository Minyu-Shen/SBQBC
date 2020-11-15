import numpy as np
import itertools
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from arena import uniform_sample_from_unit_simplex


class Region(object):
    def __init__(self, region_id, dim, vertexs, depth):
        self.region_id = region_id
        self.dim = dim
        self.vertexs = vertexs  # a list of coordinates
        self.depth = depth

        self.children = []
        self.parent = None

        # store pre-sample data
        self.pre_sample_points = []
        self.pre_sample_size = 20

    def is_pre_sample_enough(self):
        return True if len(self.pre_sample_points) >= self.pre_sample_size else False

    def pop_one_sample_point(self):
        return self.pre_sample_points.pop()

    def add_pre_sample_point(self, point):
        """ add pre-sampled point into property
        point -- a tuple of point
        """
        assert len(point) == self.dim, "dimension is mismatched"
        p_point = Point(point)
        polygon = Polygon(self.vertexs)
        assert polygon.is_valid, "polygon defined by self.vertexs should be valid"
        if polygon.contains(p_point):
            self.pre_sample_points.append(point)
            return True
        else:
            return False

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_depth(self):
        depth = 0
        p = self.parent
        while p:
            depth += 1
            p = p.parent

    def print_tree(self):
        spaces = " " * self.depth * 8
        prefix = spaces + "|______" if self.parent else ""
        print(prefix + str(self.region_id) + str(self.vertexs))
        if self.children:
            for child in self.children:
                child.print_tree()


def create_sub_region(
    parent_vertexs, parent_region_id, parent_depth, curr_region_id_count
):
    dim = len(parent_vertexs)
    # calculate the centroid
    centroid = []
    for coordinates_one_dim in zip(*parent_vertexs):
        each_dim_centroid = round(sum(coordinates_one_dim) / dim, 3)
        centroid.append(each_dim_centroid)
    centroid = tuple(centroid)
    # print("------ parent_region_id is: ", parent_region_id, "centriod is: ", centroid)

    # for each sub_region, built it
    region_id_increment_track = 0
    sub_regions = []
    for rest_vertexs in itertools.combinations(enumerate(parent_vertexs), dim - 1):
        vertexs = [()] * dim
        for each_rest_vertex in rest_vertexs:
            vertexs[each_rest_vertex[0]] = each_rest_vertex[1]
        for idx, vertex in enumerate(vertexs):
            if vertex is ():
                vertexs[idx] = centroid
                break
        region_id = curr_region_id_count + region_id_increment_track
        sub_region = Region(
            region_id=region_id, dim=dim, vertexs=vertexs, depth=parent_depth + 1
        )
        region_id_increment_track += 1
        sub_regions.append(sub_region)
    return sub_regions


def build_region_tree(dim, max_depth):
    total_region_list = []

    I = np.identity(dim)
    vertexs = [tuple(vertex) for vertex in I.tolist()]
    root_region = Region(region_id=0, dim=dim, vertexs=vertexs, depth=0)
    total_region_list.append(root_region)
    curr_region_id_count = 1
    for iter_depth in range(1, max_depth, 1):
        parent_depth = iter_depth - 1
        parent_regions = [
            region for region in total_region_list if region.depth == parent_depth
        ]
        for parent_region in parent_regions:
            sub_regions = create_sub_region(
                parent_region.vertexs,
                parent_region.region_id,
                parent_region.depth,
                curr_region_id_count,
            )
            curr_region_id_count += dim
            for sub_region in sub_regions:
                parent_region.add_child(sub_region)
            total_region_list.extend(sub_regions)

    # start uniform pre-sampling and add to property
    while True:
        a = False
        one_sample = uniform_sample_from_unit_simplex(size=1, dim=dim)
        one_sample_tuple = tuple(one_sample)
        # print(one_sample_tuple)
        for region in total_region_list:
            if region.is_pre_sample_enough():
                continue  # search check next region
            if region.add_pre_sample_point(one_sample_tuple):
                # print(region.region_id)
                break

        for region in total_region_list:
            if not region.is_pre_sample_enough():
                break
        else:
            break  # break the while True loop

    # for region in total_region_list:
    #     print(region.is_pre_sample_enough())
    # root_region.print_tree()

    return total_region_list[0]  # return the root_region
    # return total_region_list


if __name__ == "__main__":
    berth_num = 3
    max_depth = 4  # root region is located at depth-0
    # region_list = build_region_tree(dim=berth_num, max_depth=max_depth)
    root_region = build_region_tree(dim=berth_num, max_depth=max_depth)

