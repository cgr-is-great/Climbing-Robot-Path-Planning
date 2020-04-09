import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import matplotlib
from typing import Tuple, List
from tsp_solver.greedy import solve_tsp
import time

Slice = List[Tuple[int, int]]
BOARD_WIDTH = 1100                                                      # 画板长度
BOARD_HEIGHT = 780
AXIS_MARGIN = 40


def calc_connectivity(slice: np.ndarray):
    """
    计算一个slice的连通性，并且返回该slice的连通区域。
    Args:
        slice: rows. A slice of map.
    Returns:
        The connectivity number and connectivity parts.
    Examples:
        data = np.array([0,0,0,0,1,1,1,0,1,0,0,0,1,1,0,1,1,0])
        print(calc_connectivity(data))
        (4, [[4, 6], [8, 8], [12, 13], [15, 16]])
    """
    connectivity = 0
    count = 0
    start_point = 0
    end_point = 0
    begin = False
    connective_parts = []
    for i in range(len(slice)):
        if slice[i] == 1:
            count = count + 1
            begin = True
            if count == 1:
                start_point = i
        else:
            end_point = i - 1
            if begin:
                begin = False
                count = 0
                connectivity = connectivity + 1
                connective_parts.append([start_point, end_point])
        if i == len(slice) - 1 and begin:
            connectivity = connectivity + 1
            connective_parts.append([start_point, len(slice) - 1])
    return connectivity, connective_parts


def get_adjacency_matrix(parts_left, parts_right) -> np.ndarray:
    """
    Get adjacency matrix of 2 neiborhood slices.
    Args:
        slice_left: left slice
        slice_right: right slice
    Returns:
        [L, R] Adjacency matrix.
    """
    adjacency_matrix = np.zeros([len(parts_left), len(parts_right)])
    for l, lparts in enumerate(parts_left):
        for r, rparts in enumerate(parts_right):
            if min(lparts[1], rparts[1]) - max(lparts[0], rparts[0]) > 0:
                adjacency_matrix[l, r] = 1
    return adjacency_matrix


def bcd(erode_img: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Boustrophedon Cellular Decomposition
    Args:
        erode_img: [H, W], eroded map. The pixel value 0 represents obstacles and 1 for free space.
    Returns:
        [H, W], separated map. The pixel value 0 represents obstacles and others for its' cell number.
    """
    assert len(erode_img.shape) == 2, 'Map should be single channel.'
    last_connectivity = 0
    last_connectivity_parts = []
    current_cell = 1
    current_cells = []
    separate_img = np.copy(erode_img)
    for col in range(erode_img.shape[1]):
        current_slice = erode_img[:, col]
        connectivity, connective_parts = calc_connectivity(current_slice)
        if last_connectivity == 0:
            current_cells = []
            for i in range(connectivity):
                current_cells.append(current_cell)
                current_cell += 1
        elif connectivity == 0:
            current_cells = []
            continue
        else:
            adj_matrix = get_adjacency_matrix(last_connectivity_parts, connective_parts)
            new_cells = [0] * len(connective_parts)
            for i in range(adj_matrix.shape[0]):
                if np.sum(adj_matrix[i, :]) == 1:
                    new_cells[np.argwhere(adj_matrix[i, :])[0][0]] = current_cells[i]   # np.argwhere(a)返回非0的数组元组的索引，其中a是要索引数组的条件。
                # 如果上一次的某个part与这次的多个parts相联通，说明发生了IN
                elif np.sum(adj_matrix[i, :]) > 1:
                    for idx in np.argwhere(adj_matrix[i, :]):
                        new_cells[idx[0]] = current_cell
                        current_cell = current_cell + 1
            for i in range(adj_matrix.shape[1]):
                # 如果这一次的某个part与上次的多个parts相联通，说明发生了OUT
                if np.sum(adj_matrix[:, i]) > 1:
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
                # 如果这次的某个part不与上次任何一个part联通，说明发生了in
                elif np.sum(adj_matrix[:, i]) == 0:
                    new_cells[i] = current_cell
                    current_cell = current_cell + 1
            current_cells = new_cells
        # 将分区信息画在地图上。
        for cell, slice in zip(current_cells, connective_parts):
            # print(current_cells, connective_parts)
            separate_img[slice[0]:slice[1] + 1, col] = cell
            # print('Slice {}: connectivity from {} to {}'.format(col, last_connectivity, connectivity))
        last_connectivity = connectivity
        last_connectivity_parts = connective_parts
    return separate_img, current_cell


def display_separate_map(separate_map, cells, centerx, centery, nodes):
    display_img = np.empty([*separate_map.shape, 3], dtype=np.uint8)
    random_colors = np.random.randint(50, 200, [cells, 3])
    for cell_id in range(1, cells):
        display_img[separate_map == cell_id, :] = random_colors[cell_id, :]

    plt.cla()
    plt.imshow(display_img)
    plt.xlim(0, BOARD_WIDTH)
    plt.ylim(0, BOARD_HEIGHT)
    # plt.axis('off')
    for i in range(len(nodes)):
        plt.scatter(centerx[i], centery[i], marker='o', color='g')
        plt.annotate('cell{}'.format(i+1), xy=(centerx[i], centery[i]))
    for index, node in enumerate(nodes):
        if index < len(nodes) - 1:
            x = [centerx[node], centerx[nodes[index+1]]]
            y = [centery[node], centery[nodes[index+1]]]
            plt.plot(x, y, color='r')
    plt.show()
    # plt.cla()


def find_dist(x1, y1, x2, y2):
    """
    计算两点之间的距离，x1, y1, x2, y2分别为两点的横纵坐标
    """
    return (pow((x1 - x2), 2) + pow(y1 - y2, 2)) ** 0.5


def get_left_tri_matrix(xlist, ylist):
    """
    获得TSP所需要的左三角矩阵，详见https://github.com/dmishin/tsp-solver
    :param xlist: 结点的横坐标列表 -> list
    :param ylist: 结点的纵坐标列表 -> list
    return: TSP所需要的左三角矩阵
    """
    temp_list = []
    maxlength = len(xlist) - 1
    temp_numpy = np.zeros(shape=[maxlength, 1])
    for i in range(len(xlist) - 1):
        for j in range(i+1, len(xlist)):
            temp = find_dist(xlist[i], ylist[i], xlist[j], ylist[j])
            temp_list.append(temp)
        if len(temp_list) < maxlength:
            for k in range(maxlength-len(temp_list)):
                temp_list.insert(0, 0)
        temp_numpy = np.concatenate([temp_numpy, np.array([temp_list]).transpose()], axis=1)
        temp_list = []
    temp_numpy = np.delete(temp_numpy, 0, axis=1)
    left_tri_matrix = temp_numpy.tolist()

    for i in range(maxlength):
        for j in range(len(left_tri_matrix[i])-1, -1, -1):
            if left_tri_matrix[i][j] == 0:
                left_tri_matrix[i].remove(0)
    left_tri_matrix.insert(0, [])
    return left_tri_matrix


def map_process(map_array, cells):
    """
    对膨胀后的地图进行处理，主要处理内容为：
    1. 由于图片坐标与界面坐标有映射关系，先对这个关系进行对应
    2. 把每一个单元的重心坐标求出
    :param map_array: 地图矩阵，类型为二维np.array，大小为H行*W列
    :param cells: 地图被划分为单元的个数
    :return: 处理后的地图矩阵，类型为二维np.array，大小为H行*W列
    """
    map_array = np.flip(map_array, 0)
    sum_x, sum_y = 0, 0
    count = 0
    center_x, center_y = [], []
    Cells = [x for x in range(1, cells)]

    for k in range(len(Cells)):
        for i in range(map_array.shape[0]):
            for j in range(map_array.shape[1]):
                if map_array[i][j] == Cells[k]:
                    sum_x = sum_x + i
                    sum_y = sum_y + j
                    count = count + 1
        center_x.append(sum_y / float(count))
        center_y.append(sum_x / float(count))
        count = 0
        sum_x, sum_y = 0, 0
    left_tri_matrix = get_left_tri_matrix(center_x, center_y)
    shortest_path_node = solve_tsp(left_tri_matrix, endpoints=(0, len(center_x) - 1))

    return map_array, center_x, center_y, shortest_path_node


# if __name__ == '__main__':
#     img = np.array(Image.open('./map_fig/Expand/lines_rec/lines_rec_expand.png'))
#     if len(img.shape) > 2:
#         img = img[:, :, 0]
#
#     erode_img = img / np.max(img)
#     # plt.imshow(img, cmap='gray')
#     # plt.show()
#     separate_img, cells = bcd(erode_img)
#     separate_img, cx, cy = map_process(separate_img, cells)
#     print('Total cells: {}'.format(cells))
#     display_separate_map(separate_img, cells)
