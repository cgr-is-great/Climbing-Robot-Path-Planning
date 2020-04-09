import math
BOARD_WIDTH = 1100  # 画板长度
BOARD_HEIGHT = 780  # 画板宽度


def convert_to_actual_size(ratio, path_list):
    """
    将图像中的机器人轨迹点坐标转化为实际地图中的轨迹点坐标
    :param ratio: 一像素对应的厘米数
    :param path_list: 图像中的机器人轨迹点坐标列表
    :return: 实际地图中的轨迹点坐标列表
    """
    map_list, temp = [], []
    for i in range(len(path_list)):
        for j in range(len(path_list[i])):
            ans = [path_list[i][j][0] * ratio, path_list[i][j][1] * ratio]
            temp.append(ans)
        map_list.append(temp)
        temp = []
    return map_list


def cal_gradient(a, b):
    """
    计算两点之间的斜率
    :param a: A点坐标，类型为[int, int]
    :param b: B点坐标，类型为[int, int]
    :return: 斜率值
    """
    if a[0] - b[0] == 0:
        return 2 ** 31 - 1
    else:
        return (a[1] - b[1]) / (a[0] - b[0])


def arc_path1(r, a, b, c):
    """
    转弯半径较大时(r > min(|CA|, |CB|))，得到由A到B圆弧部分的轨迹点坐标，C点为原列表中A与B之间的点，需要剔除并且改为圆弧，本函数中用C点判断圆弧方向
    :param r: 转弯半径
    :param a: A点坐标，类型为[int, int]
    :param b: B点坐标，类型为[int, int]
    :param c: C点坐标，类型为[int, int]
    :return: 圆弧部分的轨迹点坐标 -> [float]
    """
    arc_path = []

    # A点与B点的中垂线Ax + By + C = 0
    A = 2 * (b[0] - a[0])
    B = 2 * (b[1] - a[1])
    C = a[0] ** 2 - b[0] ** 2 + a[1] ** 2 - b[1] ** 2

    if A == 0 and B != 0:                                               # 若A = 0，则中垂线平行于横轴
        r_y = (a[1] + b[1]) / 2
        if c[0] > a[0]:
            r_x = a[0] - (r ** 2 - ((b[1] - a[1]) / 2) ** 2) ** 0.5
        else:
            r_x = a[0] + (r ** 2 - ((b[1] - a[1]) / 2) ** 2) ** 0.5
    elif A != 0 and B == 0:                                             # 若B = 0，则中垂线垂直于横轴
        r_x = (a[0] + b[0]) / 2
        if c[1] > a[1]:
            r_y = a[1] - (r ** 2 - ((b[0] - a[0]) / 2) ** 2) ** 0.5
        else:
            r_y = a[1] + (r ** 2 - ((b[0] - a[0]) / 2) ** 2) ** 0.5
    else:                                                               # A与B均不为0，一般直线
        mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        k = -A / B
        d = (r ** 2 - ((mid[0] - a[0]) ** 2 + (mid[1] - a[1]) ** 2)) ** 0.5
        r_x1, r_x2 = mid[0] - d / ((k * k + 1) ** 0.5), mid[0] + d / ((k * k + 1) ** 0.5)
        r_y1, r_y2 = k * r_x1 - C / B, k * r_x2 - C / B
        # 采用面积法判断C点与圆心是否在直线同一侧，应选取异侧的为圆心，即圆心与要剔除的C点应该在线段ab的两侧
        S_c = (a[0] - c[0]) * (b[1] - c[1]) - (a[1] - c[1]) * (b[0] - c[0])
        S_1 = (a[0] - r_x1) * (b[1] - r_y1) - (a[1] - r_y1) * (b[0] - r_x1)
        S_2 = (a[0] - r_x2) * (b[1] - r_y2) - (a[1] - r_y2) * (b[0] - r_x2)
        if S_c * S_1 > 0:
            r_x, r_y = r_x2, r_y2
        elif S_c * S_2 > 0:
            r_x, r_y = r_x1, r_y1
    theta = math.acos(((a[0] - r_x) * (b[0] - r_x) + (a[1] - r_y) * (b[1] - r_y)) / (r * r))
    theta = abs(theta) / 10
    theta_a = math.acos((a[0] - r_x) / r)
    S_ab = (a[0] - r_x) * (b[1] - r_y) - (a[1] - r_y) * (b[0] - r_x)
    if S_ab > 0:                                    # 弧ab为顺时针
        if a[1] > r_y:
            theta_a = 2 * math.pi - theta_a
        for i in range(1, 10):
            temp_x = r_x + r * math.cos(theta_a - theta * i)
            temp_y = r_y - r * math.sin(theta_a - theta * i)
            arc_path.append([temp_x, temp_y])
    else:
        if a[1] > r_y:
            theta_a = 2 * math.pi - theta_a
        for i in range(1, 10):                      # 弧ab为逆时针
            temp_x = r_x + r * math.cos(theta_a + theta * i)
            temp_y = r_y - r * math.sin(theta_a + theta * i)
            arc_path.append([temp_x, temp_y])
    return arc_path


def arc_path2(r, a, b, c):
    """
    转弯半径较小时(r < min(|CA|, |CB|))，得到由A到B圆弧部分的轨迹点坐标，C点为原列表中A与B之间的点，需要剔除并且改为圆弧，本函数中用C点判断圆弧方向
    :param r: 转弯半径
    :param a: A点坐标，类型为[int, int]
    :param b: B点坐标，类型为[int, int]
    :param c: C点坐标，类型为[int, int]
    :return: 圆弧部分的轨迹点坐标 -> [float]
    """
    arc_path = []
    ca, cb = [a[0] - c[0], a[1] - c[1]], [b[0] - c[0], b[1] - c[1]]
    theta = math.acos((ca[0] * cb[0] + ca[1] * cb[1]) / (((ca[0] ** 2 + ca[1] ** 2) ** 0.5) * ((cb[0] ** 2 + cb[1] ** 2) ** 0.5)))
    theta1 = theta / 2
    l = r / math.tan(theta1)
    theta2 = math.acos(ca[0] / ((ca[0] ** 2 + ca[1] ** 2) ** 0.5))
    d = [c[0] + l * math.cos(theta2), c[1] + l * math.sin(theta2) * ((-1) ** ((a[1] > c[1]) + 1))]
    theta3 = math.pi - theta
    theta3 = theta3 / 10
    theta4 = theta2 - 0.5 * math.pi
    r_x1, r_y1 = d[0] + r * math.cos(theta4), d[1] - r * math.sin(theta4)
    r_x2, r_y2 = d[0] - r * math.cos(theta4), d[1] + r * math.sin(theta4)
    S_b = (a[0] - b[0]) * (c[1] - b[1]) - (a[1] - b[1]) * (c[0] - b[0])
    S_1 = (a[0] - r_x1) * (c[1] - r_y1) - (a[1] - r_y1) * (c[0] - r_x1)
    S_2 = (a[0] - r_x2) * (c[1] - r_y2) - (a[1] - r_y2) * (c[0] - r_x2)
    if S_b * S_1 > 0:
        r_x, r_y = r_x1, r_y1
    elif S_b * S_2 > 0:
        r_x, r_y = r_x2, r_y2
    rd = [d[0] - r_x, d[1] - r_y]
    theta5 = math.acos(rd[0] / ((rd[0] ** 2 + rd[1] ** 2) ** 0.5))

    if S_b > 0:                                     # 弧ab为顺时针
        if d[1] > r_y:
            theta5 = 2 * math.pi - theta5
        for i in range(11):
            temp_x = r_x + r * math.cos(theta5 - theta3 * i)
            temp_y = r_y - r * math.sin(theta5 - theta3 * i)
            arc_path.append([temp_x, temp_y])
    else:
        if d[1] > r_y:
            theta5 = 2 * math.pi - theta5
        for i in range(11):                      # 弧ab为逆时针
            temp_x = r_x + r * math.cos(theta5 + theta3 * i)
            temp_y = r_y - r * math.sin(theta5 + theta3 * i)
            arc_path.append([temp_x, temp_y])
    return arc_path


def smooth_path(map_list, r):
    """
    将轨迹平滑处理，即去掉尖锐转角点
    :param map_list: 实际地图中的轨迹点坐标列表
    :param r: 转弯半径
    :return: 平滑处理后的实际地图中的轨迹点坐标列表
    """
    # MAP_WIDTH, MAP_HEIGHT = BOARD_WIDTH * ratio, BOARD_HEIGHT * ratio
    for i in range(len(map_list)):
        j = 1
        flag = 0
        while j < len(map_list[i]) - 1:
            if j + 1 < len(map_list[i]):
                if flag == 0:
                    if cal_gradient(map_list[i][j - 1], map_list[i][j]) != cal_gradient(map_list[i][j], map_list[i][j + 1]):
                        flag = 1
                        ans1 = ((map_list[i][j][0] - map_list[i][j - 1][0]) ** 2 + (map_list[i][j][1] - map_list[i][j - 1][1]) ** 2) ** 0.5
                        ans2 = ((map_list[i][j][0] - map_list[i][j + 1][0]) ** 2 + (map_list[i][j][1] - map_list[i][j + 1][1]) ** 2) ** 0.5
                        if r > min(ans1, ans2):
                            temp = arc_path1(r, map_list[i][j - 1], map_list[i][j + 1], map_list[i][j])
                        else:
                            temp = arc_path2(r, map_list[i][j - 1], map_list[i][j + 1], map_list[i][j])
                        map_list[i].remove(map_list[i][j])
                        for k in range(len(temp)):
                            map_list[i].insert(j + k, temp[k])
                        j = j + len(temp)
                    else:
                        j = j + 1
                else:
                    flag = 0
    return map_list


# r = 0.5
# a = [[[1, 1], [1, 3], [1, 5], [1, 7], [2, 7], [2, 5], [2, 3], [2, 1], [3, 1], [3, 2], [3, 3], [4, 3]],
#      [[8, 4], [8, 5], [8, 6], [8, 7], [9, 7], [9, 6], [9, 5], [9, 4], [10, 4], [10, 3], [10, 2]]]
# b = smooth_path(a, r)
# print(b)
# a = [1, 1]
# b = [6, 4]
# c = [2, 3]
# a = [4, 1]
# b = [2, 4]
# c = [5, 3]
# a = [2, 3]
# b = [3, 1]
# c = [2, 1]
# #
# d = arc_path2(r, a, b, c)
