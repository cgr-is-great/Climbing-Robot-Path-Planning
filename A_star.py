BOARD_WIDTH = 1100                                                      # 画板长度
BOARD_HEIGHT = 780                                                      # 画板宽度
OBSTACLE = 0                                                            # 障碍物
NORMAL = 1                                                              # 空点


class Item:
    """
    每一个像素点的属性，包括坐标，状态（障碍物、可通行点、起点、终点）
    """
    def __init__(self, x, y, status):
        self.x = x
        self.y = y
        self.status = status
        self.mf = -1
        self.mg = -1
        self.mh = -1
        self.mParent = None
        self.isPath = 0


def init_map(erode_img):
    """
    初始化地图中各个像素点的状态信息
    """
    MAP = []
    for h in range(BOARD_HEIGHT):
        for w in range(BOARD_WIDTH):
            MAP.append(Item(w, h, erode_img[h][w]))
    return MAP


def cal_g(point, min_fpoint):
    """
    计算点point的g值，即从起点沿着到达该点而生成的路径移动到point的移动代价。
    :param point: Item类型，所要计算的点
    :param min_fpoint: Item类型，F值最小的点
    :return: 计算得到的g值
    """
    return ((point.x - point.mParent.x) ** 2 + (point.y - point.mParent.y) ** 2) ** 0.5 + min_fpoint.mg


def cal_f(point, end_point):
    """
    计算点point的f值，f=g+h，h即从指定的点移动到终点的估算代价
    :param point: Item类型，所要计算的点
    :param end_point: 终点
    :return: 计算得到的f值
    """
    h = abs(end_point.x - point.x) + abs(end_point.y - point.y)
    g = 0
    if point.mParent is None:
        g = 0
    else:
        g = point.mParent.mg + ((point.x - point.mParent.x) ** 2 + (point.y - point.mParent.y) ** 2) ** 0.5
    point.mg = g
    point.mh = h
    point.mf = g + h
    return


def not_obstacle_and_close(point, close_list):
    """
    不能是障碍块，不包含在关闭列表中
    """
    if point not in close_list and point.status != OBSTACLE:
        return True
    return False


def find_point_with_min_f(open_list):
    """
    查找open_list中最小的f值
    """
    f = 0xffffff
    temp = None
    for pc in open_list:
        if pc.mf < f:
            temp = pc
            f = pc.mf
    return temp


def find_surround_point(point, close_list, Map):
    """
    查找周围块
    """
    surround_list = []
    up, down, left, right = None, None, None, None
    left_up, right_up, left_down, right_down = None, None, None, None

    if point.y > 0:                                                     # 上方的点
        up = Map[BOARD_WIDTH * (point.y - 1) + point.x]
        if not_obstacle_and_close(up, close_list):
            surround_list.append(up)
    if point.y < BOARD_HEIGHT - 1:                                      # 下方的点
        down = Map[BOARD_WIDTH * (point.y + 1) + point.x]
        if not_obstacle_and_close(down, close_list):
            surround_list.append(down)
    if point.x > 0:                                                     # 左侧的点
        left = Map[BOARD_WIDTH * point.y + point.x - 1]
        if not_obstacle_and_close(left, close_list):
            surround_list.append(left)
    if point.x < BOARD_WIDTH - 1:                                       # 右侧的点
        right = Map[BOARD_WIDTH * point.y + point.x + 1]
        if not_obstacle_and_close(right, close_list):
            surround_list.append(right)
    # 斜方向的点还需考虑对应正方向不是障碍物
    if point.x > 0 and point.y > 0:                                     # 左上角的点
        left_up = Map[BOARD_WIDTH * (point.y - 1) + point.x - 1]
        if not_obstacle_and_close(left_up, close_list) and left.status != OBSTACLE and up.status != OBSTACLE:
            surround_list.append(left_up)
    if point.x < BOARD_WIDTH - 1 and point.y > 0:                       # 右上角的点
        right_up = Map[BOARD_WIDTH * (point.y - 1) + point.x + 1]
        if not_obstacle_and_close(right_up, close_list) and right.status != OBSTACLE and up.status != OBSTACLE:
            surround_list.append(right_up)
    if point.x > 0 and point.y < BOARD_HEIGHT - 1:                      # 左下角的点
        left_down = Map[BOARD_WIDTH * (point.y + 1) + point.x - 1]
        if not_obstacle_and_close(left_down, close_list) and left.status != OBSTACLE and down.status != OBSTACLE:
            surround_list.append(left_down)
    if point.x < BOARD_WIDTH - 1 and point.y < BOARD_HEIGHT - 1:        # 右下角的点
        right_down = Map[BOARD_WIDTH * (point.y + 1) + point.x + 1]
        if not_obstacle_and_close(right_down, close_list) and right.status != OBSTACLE and down.status != OBSTACLE:
            surround_list.append(right_down)
    return surround_list


def find_path(start, end, Map):
    """
    利用A*寻找路径
    """
    open_list, close_list = [], []                                      # 开启列表以及关闭列表
    final_a_star = []                                                   # 最终的A*轨迹
    start_num = start[1] * BOARD_WIDTH + start[0]
    end_num = end[1] * BOARD_WIDTH + end[0]
    open_list.append(Map[start_num])                                    # 开启列表插入起始点

    while len(open_list) > 0:
        min_f_point = find_point_with_min_f(open_list)                  # 寻找开启列表中最小预算值的点
        open_list.remove(min_f_point)                                   # 从开启列表移除
        close_list.append(min_f_point)                                  # 添加到关闭列表
        surround_list = find_surround_point(min_f_point, close_list, Map)    # 找到当前点周围点
        for sp in surround_list:                                        # 开始寻路
            if sp in open_list:                          # 存在在开启列表，说明上一块查找时并不是最优路径，考虑此次移动是否是最优路径
                new_g = cal_g(sp, min_f_point)                          # 计算新路径下的G值
                if new_g < sp.mg:
                    sp.mg = new_g
                    sp.mf = sp.mg + sp.mh
                    sp.mParent = min_f_point
            else:
                sp.mParent = min_f_point                                # 当前查找到点指向上一个节点
                cal_f(sp, Map[end_num])
                open_list.append(sp)
        if Map[end_num] in open_list:
            Map[end_num].mParent = min_f_point
            break
    cur_point = Map[end_num]
    while True:
         cur_point.isPath = 1
         cur_point = cur_point.mParent
         if cur_point is None:
            break
         if cur_point.mParent is not None and cur_point.mParent.mParent == cur_point:
            break
    for i in range(len(close_list)):
        if close_list[i].isPath == 1:
            final_a_star.append(close_list[i])
    return final_a_star


def a_star(erode_img, start_end_list):
    """
    A*算法，生成各个单元之间切换时上一单元的终点到下一单元的起点之间的点到点路径
    :param erode_img: 0-1图像矩阵
    :param start_end_list: 各个单元内部起点终点坐标列表
    :return: 插入过单元间切换轨迹的完整覆盖轨迹
    """
    Map = init_map(erode_img)
    new_map = Map
    temp1, temp2, a_star_list = [], [], []
    for i in range(1, len(start_end_list) - 1):
        if i % 2 == 1:
            start, end = start_end_list[i], start_end_list[i + 1]
            temp1 = find_path(start, end, new_map)
            for j in range(len(temp1)):
                temp2.append([temp1[j].x, temp1[j].y])
        if temp2:
            a_star_list.append(temp2)
        temp1, temp2 = [], []
    return a_star_list


def final_list(path_list, a_star_list):
    """
    将两个轨迹合成为一个轨迹
    """
    for i in range(len(path_list) - 1):
        path_list.insert(2 * i + 1, a_star_list[i])
    return path_list
