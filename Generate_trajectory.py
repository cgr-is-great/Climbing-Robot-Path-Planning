import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import Cellular_Decomposition
import cv2

BOARD_WIDTH = 1100                                                      # 画板长度
BOARD_HEIGHT = 780                                                      # 画板宽度


def deleteDuplicatedElementFromList(List):
    resultList = []
    for item in List:
        if not item in resultList:
            resultList.append(item)
    return resultList


def find_point(map_array, cells, path_node, length, width, ratio, coefficient):
    """
    寻找一幅图片中除了障碍物之外各个单元的四个角点并返回坐标
    :param map_array: 要提取角点的图片
    :param cells: 单元总数目
    :param path_node: TSP确定的单元遍历顺序列表
    :param length: 机器人长度
    :param width: 机器人宽度
    :param ratio: 实际长度与像素的比例
    :param width: 机器人宽度
    :param coefficient: 膨胀调节系数
    """
    map_array = np.flip(map_array, 0)
    distance = int(coefficient * (min(length, width) / ratio) / 2)          # 根据机器人尺寸计算得到的像素距离
    temp = []
    for i in range(1, cells):
        temp.append(np.argwhere(map_array == i))
    start_cell = path_node[0] + 1
    end_cell = path_node[len(path_node) - 1] + 1
    down_l_point, down_r_point, up_l_point, up_r_point = [], [], [], []
    for i in range(len(temp)):
        lef = temp[i].min(axis=0)[1]
        righ = temp[i].max(axis=0)[1]

        down_l = temp[i][np.argwhere(temp[i] == lef).max(axis=0)][0][0]
        down_r = temp[i][np.argwhere(temp[i] == righ).max(axis=0)][0][0]
        up_l = temp[i][np.argwhere(temp[i] == lef).min(axis=0)][0][0]
        up_r = temp[i][np.argwhere(temp[i] == righ).min(axis=0)][0][0]

        d_l_point = [lef + distance, down_l - distance]
        d_r_point = [righ - distance, down_r - distance]
        u_l_point = [lef + distance, up_l + distance]
        u_r_point = [righ - distance, up_r + distance]

        down_l_point.append(d_l_point)
        down_r_point.append(d_r_point)
        up_l_point.append(u_l_point)
        up_r_point.append(u_r_point)
    # 绘制所有单元的四个角点
    # for i in range(len(down_l_point)):
    #     plt.scatter(down_l_point[i][0], BOARD_HEIGHT - 1 - down_l_point[i][1], marker='*', color='w')
    #     plt.scatter(down_r_point[i][0], BOARD_HEIGHT - 1 - down_r_point[i][1], marker='*', color='b')
    #     plt.scatter(up_l_point[i][0], BOARD_HEIGHT - 1 - up_l_point[i][1], marker='*', color='g')
    #     plt.scatter(up_r_point[i][0], BOARD_HEIGHT - 1 - up_r_point[i][1], marker='*', color='y')
    # 在每一单元的四个角点与下一单元的四个角点之间寻找距离最短的组合，以此确定该单元的终点与下一单元的起点
    start_end_list, temp1 = [], []
    for i in range(len(path_node) - 1):
        cur_index = path_node[i]
        nex_index = path_node[i + 1]
        current_end, next_start = cal_min_distance(down_l_point[cur_index], down_r_point[cur_index], up_l_point[cur_index], up_r_point[cur_index],
                                                   down_l_point[nex_index], down_r_point[nex_index], up_l_point[nex_index], up_r_point[nex_index])
        temp1.append([current_end, next_start])
    for i in range(len(temp1)):
        start_end_list.append(temp1[i][0])
        start_end_list.append(temp1[i][1])
    # start_end_list即为从起始单元的终点到结尾单元的起点的组合列表，长度为(len(path_node) - 1) * 2
    # 下一步是确定起始单元的起点即全局起点，以及结尾单元的终点即全局终点
    # 先找全局起点，即在起始单元左下角点
    start_end_list.insert(0, [down_l_point[start_cell - 1][0], down_l_point[start_cell - 1][1]])
    # 再找全局终点，即在最末单元右下角点
    start_end_list.append([down_r_point[end_cell - 1][0], down_r_point[end_cell - 1][1]])
    # 加上全局终点与起点后，start_end_list长度为len(path_node) * 2
    for i in range(len(start_end_list)):
        if i % 2 == 0:
            plt.scatter(start_end_list[i][0], BOARD_HEIGHT - 1 - start_end_list[i][1], marker='>', color='r')
        else:
            plt.scatter(start_end_list[i][0], BOARD_HEIGHT - 1 - start_end_list[i][1], marker='<', color='k')
    # 下一步即为在每一个单元内生成覆盖轨迹
    path_list, path_list_incell = [], []
    dis = int(coefficient * (min(length, width) / ratio))
    for i in range(len(path_node)):
        d_hor = max(abs(down_l_point[path_node[i]][0] - down_r_point[path_node[i]][0]),
                    abs(up_l_point[path_node[i]][0] - up_r_point[path_node[i]][0])) + dis               # 起点与终点水平距离
        d_ver = max(abs(up_l_point[path_node[i]][1] - down_l_point[path_node[i]][1]),
                    abs(up_r_point[path_node[i]][1] - down_r_point[path_node[i]][1])) + dis             # 起点与终点垂直距离
        n_hor = int(d_hor / dis)                                                                        # 水平方向机器人宽度个数
        n_ver = int(d_ver / dis)                                                                        # 垂直方向机器人宽度个数
        if n_hor < 1 or n_ver < 1:
            break
        Temp = [down_l_point[path_node[i]], down_r_point[path_node[i]], up_l_point[path_node[i]], up_r_point[path_node[i]]]
        turn_flag = 0
        corner_index = Temp.index(start_end_list[2 * i])                            # corner_index为0, 1, 2, 3时对应起点在左下，右下，左上，右上角
        x = start_end_list[2 * i][1]
        y = start_end_list[2 * i][0]
        if d_hor < d_ver:                                                           # 如果起点与终点水平距离小于垂直距离
            for m in range(n_hor + 1):
                if m != 0:
                    y = y + ((-1) ** (corner_index % 2)) * dis                      # corner_index为0, 2时起点在左侧，y应该增加；反之在右侧，y应该减小
                for k in range(n_ver + 1):
                    if k != 0:
                        x = int(x + ((-1) ** (m + (1 - int(corner_index / 2)))) * dis)   # corner_index为0, 1时起点在下方，上下上下循环；反之在上方，下上下上循环
                    if x > max(down_l_point[path_node[i]][1], down_r_point[path_node[i]][1]):
                        x = max(down_l_point[path_node[i]][1], down_r_point[path_node[i]][1])
                    elif x < min(up_l_point[path_node[i]][1], up_r_point[path_node[i]][1]):
                        x = min(up_l_point[path_node[i]][1], up_r_point[path_node[i]][1])
                    elif y < min(up_l_point[path_node[i]][0], down_l_point[path_node[i]][0]):
                        y = min(up_l_point[path_node[i]][0], down_l_point[path_node[i]][0])
                    elif y > max(down_r_point[path_node[i]][0], up_r_point[path_node[i]][0]):
                        y = max(down_r_point[path_node[i]][0], up_r_point[path_node[i]][0])
                    if turn_flag == 0:
                        if map_array[x][y] == path_node[i] + 1:
                            path_list_incell.append([y, x])
                        else:
                            turn_flag = 1
                            break
                    else:
                        if map_array[x][y] == path_node[i] + 1:
                            path_list_incell.append([y, x])
                            turn_flag = 0
                        else:
                            turn_flag = 1
            path_list_incell.append(start_end_list[2 * i + 1])
            path_list.append(path_list_incell)
            show_path(path_list_incell)
            path_list_incell = []
        else:
            for m in range(n_ver + 1):
                if m != 0:
                    x = x + ((-1) ** (1 - int(corner_index / 2))) * dis                  # corner_index为0, 1时起点在下方，x应该增加；反之在上方，x应该减小
                for k in range(n_hor + 1):
                    if k != 0:
                        y = y + ((-1) ** (m + corner_index % 2)) * dis                       # corner_index为0, 2时起点在左侧，右左循环；反之在右侧，左右循环
                    if x > max(down_l_point[path_node[i]][1], down_r_point[path_node[i]][1]):
                        x = max(down_l_point[path_node[i]][1], down_r_point[path_node[i]][1])
                    elif x < min(up_l_point[path_node[i]][1], up_r_point[path_node[i]][1]):
                        x = min(up_l_point[path_node[i]][1], up_r_point[path_node[i]][1])
                    elif y < min(up_l_point[path_node[i]][0], down_l_point[path_node[i]][0]):
                        y = min(up_l_point[path_node[i]][0], down_l_point[path_node[i]][0])
                    elif y > max(down_r_point[path_node[i]][0], up_r_point[path_node[i]][0]):
                        y = max(down_r_point[path_node[i]][0], up_r_point[path_node[i]][0])
                    if turn_flag == 0:
                        if map_array[x][y] == path_node[i] + 1:
                            path_list_incell.append([y, x])
                        else:
                            turn_flag = 1
                            break
                    else:
                        if map_array[x][y] == path_node[i] + 1:
                            path_list_incell.append([y, x])
                            turn_flag = 0
                        else:
                            turn_flag = 1
            path_list_incell.append(start_end_list[2 * i + 1])
            path_list.append(path_list_incell)
            show_path(path_list_incell)
            path_list_incell = []
    plt.show()
    return


def cal_distance(point1, point2):
    """
    计算平面两点之间距离, point1与point2均为1*2列表
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def cal_min_distance(point1, point2, point3, point4, point5, point6, point7, point8):
    """
    计算point1——point4与point5——point8之间距离的最小值，共4*4=16种可能性中寻找最小值，并返回哪一个点和哪一个点距离最小
    """
    distance_list = []
    Point1, Point2 = [point1, point2, point3, point4], [point5, point6, point7, point8]
    for i in range(4):
        for j in range(4):
            distance_list.append(cal_distance(Point1[i], Point2[j]))
    min_index = distance_list.index(min(distance_list))
    index1 = int(min_index / 4)
    index2 = min_index % 4
    return Point1[index1], Point2[index2]


def show_path(path_list):
    for i in range(len(path_list) - 1):
        x = [path_list[i][0], path_list[i+1][0]]
        y = [BOARD_HEIGHT - 1 - path_list[i][1], BOARD_HEIGHT - 1 - path_list[i+1][1]]
        plt.scatter(x[0], y[0], marker='.', color='k')
        plt.plot(x, y, 'k--')
    plt.scatter(path_list[len(path_list) - 1][0], BOARD_HEIGHT - 1 - path_list[len(path_list) - 1][1], marker='.', color='k')

# def find_point():
#     img = cv2.imread('a.png')
#     gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#     gray = np.float32(gray)    #将gray转化为float32的输入图像 blocksize=2，ksize=3
#     dst = cv2.cornerHarris(gray,2,3,0.04)
#     dst = cv2.dilate(dst,None)
#     img[dst>0.01*dst.max()]=[0,0,255]
#     cv2.imshow('cornerHarris',img)
#     if cv2.waitKey(0) & 0xff == 27:
#         cv2.destroyAllWindows()
