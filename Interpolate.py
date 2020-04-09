import numpy as np
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt

BOARD_WIDTH = 1100                                                      # 画板长度
BOARD_HEIGHT = 780                                                      # 画板宽度
AXIS_MARGIN = 40
fig_path_rec = ".\\map_fig\\No_Expand\\rec\\"                           # 未膨胀矩形障碍物轮廓图片保存路径
fig_path_lines = ".\\map_fig\\No_Expand\\lines\\"                       # 未膨胀折线障碍物轮廓图片保存路径
fig_path_lines_rec = ".\\map_fig\\No_Expand\\lines_rec\\"               # 未膨胀矩形+折线障碍物轮廓图片保存路径


def Interpolate_Line(trajectory, kind='linear'):
    """
    直线轨迹与手绘轨迹插值模块
    :param trajectory: 轨迹列表
    :param kind: 插值种类
    :return: 插值后的轨迹坐标点序列
    """
    x_arr = []
    y_arr = []
    if len(trajectory) == 0:
        return []
    for point in trajectory:
        x_arr.append(point.x())
        y_arr.append(point.y())
    f1 = interp1d(np.array(x_arr), np.array(y_arr), kind=kind)              # scipy的1维插值函数
    x_pred = np.linspace(min(x_arr), max(x_arr), 5 * len(x_arr))
    y_pred = f1(x_pred)

    plt.plot(x_pred, y_pred, 'r.')
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()
    t_pred = []
    for i in range(len(x_pred)):
        t_pred.append([x_pred[i], y_pred[i]])
    return t_pred


def Interpolate_Lines(trajectory, trajectory_flag):
    """
    折线框选障碍物模块，未按下中键，说明一直在框选一个障碍物，无需打断，按下了中键，则切换了障碍物，需要在轨迹序列trajectory中做出标记
    :param trajectory: 轨迹列表
    :param trajectory_flag: 轨迹中断的标记列表
    :return: 轨迹列表
    """
    x_arr = []
    y_arr = []
    x_temp = []
    y_temp = []
    x_draw = []
    y_draw = []
    t_temp = []
    t_pred = []
    if len(trajectory) == 0:
        return []
    for point in trajectory:
        x_arr.append(BOARD_WIDTH - AXIS_MARGIN - point.x())
        y_arr.append(point.y())
    for i in range(len(x_arr)):
        if i not in trajectory_flag:
            x_temp.append(x_arr[i])
            y_temp.append(y_arr[i])
        else:
            x_draw.append(x_temp)
            y_draw.append(y_temp)
            x_temp = []
            y_temp = []
            x_temp.append(x_arr[i])
            y_temp.append(y_arr[i])
        if i == len(x_arr) - 1:
            x_draw.append(x_temp)
            y_draw.append(y_temp)

    for i in range(len(x_draw)):
        print(x_draw[i])
        print(y_draw[i])
        plt.fill(x_draw[i], y_draw[i], facecolor='k')
    plt.xlim(0, BOARD_WIDTH)
    plt.ylim(0, BOARD_HEIGHT)
    plt.axis('off')
    fig = plt.gcf()
    fig.set_size_inches(float(BOARD_WIDTH) / 100, float(BOARD_HEIGHT) / 100)                    # dpi = 100, output = BOARD_WIDTH*BOARD_HEIGHT pixels
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    fig.savefig(fname=fig_path_lines+'lines.png', dpi=100, pad_inches=0, transparent=True)
    plt.cla()
    # plt.show()
    for i in range(len(trajectory_flag)):
        if i == 0:
            for j in range(trajectory_flag[i]):
                t_temp.append([x_arr[j], y_arr[j]])
        else:
            for j in range(trajectory_flag[i] - trajectory_flag[i-1]):
                t_temp.append([x_arr[j+trajectory_flag[i-1]], y_arr[j+trajectory_flag[i-1]]])
        t_pred.append(t_temp)
        t_temp = []
    return t_pred


def Interpolate_Cycle(trajectory):
    """
    圆形轨迹插值模块
    :param trajectory: 轨迹列表
    :return: 插值后的轨迹坐标点序列
    """
    x_arr = []
    y_arr = []
    if len(trajectory) == 0:
        return []
    for point in trajectory:
        x_arr.append(point.x())
        y_arr.append(point.y())

    plt.plot(x_arr, y_arr, 'r.')
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()

    t_pred = []
    for i in range(len(x_arr)):
        t_pred.append([x_arr[i], y_arr[i]])
    return t_pred


def Interpolate_Rec(trajectory):
    """
    矩形框选模块
    :param trajectory: 轨迹列表
    :return: 矩形各顶点坐标
    """
    x_arr = []
    y_arr = []
    x_draw = []
    y_draw = []
    if len(trajectory) == 0:
        return []
    for point in trajectory:
        x_arr.append(BOARD_WIDTH - AXIS_MARGIN - point.x())
        y_arr.append(point.y())
    for i in range(int(len(trajectory) / 2)):
        x_draw.append(x_arr[i * 2])
        x_draw.append(x_arr[i * 2 + 1])
        x_draw.append(x_arr[i * 2 + 1])
        x_draw.append(x_arr[i * 2])

        y_draw.append(y_arr[i * 2 + 1])
        y_draw.append(y_arr[i * 2 + 1])
        y_draw.append(y_arr[i * 2])
        y_draw.append(y_arr[i * 2])
    x_draw = np.array(x_draw).reshape(-1, 4)
    y_draw = np.array(y_draw).reshape(-1, 4)
    for i in range(x_draw.shape[0]):
        print(x_draw[i])
        print(y_draw[i])
        plt.fill(x_draw[i], y_draw[i], facecolor='k')
    plt.xlim(0, BOARD_WIDTH)
    plt.ylim(0, BOARD_HEIGHT)
    plt.axis('off')
    fig = plt.gcf()
    fig.set_size_inches(float(BOARD_WIDTH) / 100, float(BOARD_HEIGHT) / 100)                     # dpi = 100, output = BOARD_WIDTH*BOARD_HEIGHT pixels
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    # plt.show()
    fig.savefig(fname=fig_path_rec+'rec.png', dpi=100, pad_inches=0, transparent=True)
    plt.cla()
    t_pred = []
    t_temp = []
    for i in range(x_draw.shape[0]):
        for j in range(4):
            t_temp.append([x_draw[i][j], y_draw[i][j]])
        t_pred.append(t_temp)
        t_temp = []
    return t_pred


def Interpolate_Rec_Lines(trajectory_rec, trajectory_lines, trajectory_flag):
    """
    矩形框选+折线框选模块
    :param trajectory_rec: 矩形障碍物轮廓列表
    :param trajectory_lines：折线框选障碍物轮廓列表
    :param trajectory_flag：轨迹中断的标记列表
    """
    # 矩形障碍物坐标计算
    x_arr_rec = []
    y_arr_rec = []
    x_draw_rec = []
    y_draw_rec = []
    if len(trajectory_rec) == 0 or len(trajectory_lines) == 0:
        return []
    for point in trajectory_rec:
        x_arr_rec.append(BOARD_WIDTH - AXIS_MARGIN - point.x())
        y_arr_rec.append(point.y())
    for i in range(int(len(trajectory_rec) / 2)):
        x_draw_rec.append(x_arr_rec[i * 2])
        x_draw_rec.append(x_arr_rec[i * 2 + 1])
        x_draw_rec.append(x_arr_rec[i * 2 + 1])
        x_draw_rec.append(x_arr_rec[i * 2])
        y_draw_rec.append(y_arr_rec[i * 2 + 1])
        y_draw_rec.append(y_arr_rec[i * 2 + 1])
        y_draw_rec.append(y_arr_rec[i * 2])
        y_draw_rec.append(y_arr_rec[i * 2])
    x_draw_rec = np.array(x_draw_rec).reshape(-1, 4)
    y_draw_rec = np.array(y_draw_rec).reshape(-1, 4)
    # 折线障碍物坐标计算
    x_arr_lines, y_arr_lines = [], []
    x_temp, y_temp = [], []
    x_draw_lines, y_draw_lines = [], []
    t_temp = []
    t_pred_rec, t_pred_lines = [], []
    t_pred = []
    for point in trajectory_lines:
        x_arr_lines.append(BOARD_WIDTH - AXIS_MARGIN - point.x())
        y_arr_lines.append(point.y())
    for i in range(len(x_arr_lines)):
        if i not in trajectory_flag:
            x_temp.append(x_arr_lines[i])
            y_temp.append(y_arr_lines[i])
        else:
            x_draw_lines.append(x_temp)
            y_draw_lines.append(y_temp)
            x_temp = []
            y_temp = []
            x_temp.append(x_arr_lines[i])
            y_temp.append(y_arr_lines[i])
        if i == len(x_arr_lines) - 1:
            x_draw_lines.append(x_temp)
            y_draw_lines.append(y_temp)
    # 地图绘制
    for i in range(x_draw_rec.shape[0]):
        print(x_draw_rec[i])
        print(y_draw_rec[i])
        plt.fill(x_draw_rec[i], y_draw_rec[i], facecolor='k')
    for i in range(len(x_draw_lines)):
        print(x_draw_lines[i])
        print(y_draw_lines[i])
        plt.fill(x_draw_lines[i], y_draw_lines[i], facecolor='k')
    plt.xlim(0, BOARD_WIDTH)
    plt.ylim(0, BOARD_HEIGHT)
    plt.axis('off')
    fig = plt.gcf()
    fig.set_size_inches(float(BOARD_WIDTH) / 100, float(BOARD_HEIGHT) / 100)                     # dpi = 100, output = BOARD_WIDTH*BOARD_HEIGHT pixels
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0, 0)
    # plt.show()
    fig.savefig(fname=fig_path_lines_rec+'lines_rec.png', dpi=100, pad_inches=0, transparent=True)
    plt.cla()
    # 障碍物坐标保存
    for i in range(x_draw_rec.shape[0]):
        for j in range(4):
            t_temp.append([x_draw_rec[i][j], y_draw_rec[i][j]])
        t_pred_rec.append(t_temp)
        t_temp = []
    t_temp = []
    for i in range(len(trajectory_flag)):
        if i == 0:
            for j in range(trajectory_flag[i]):
                t_temp.append([x_arr_lines[j], y_arr_lines[j]])
        else:
            for j in range(trajectory_flag[i] - trajectory_flag[i-1]):
                t_temp.append([x_arr_lines[j+trajectory_flag[i-1]], y_arr_lines[j+trajectory_flag[i-1]]])
        t_pred_lines.append(t_temp)
        t_temp = []
    t_pred.append(t_pred_rec)
    t_pred.append(t_pred_lines)
    return t_pred
