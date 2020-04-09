import math
import numpy as np
import matplotlib.pyplot as plt

show_gif = True


class Config:
    """
    用于仿真的参数
    """
    def __init__(self):
        self.max_speed = 50                                     # 最大线速度
        self.min_speed = 0                                      # 最小线速度
        self.max_rate = math.pi / 2                             # 最大角速度
        self.min_rate = -math.pi / 2                            # 最小角速度
        self.max_acc_speed = 25                                 # 最大加速度
        self.max_acc_rate = math.pi / 4                         # 最大角加速度
        self.dv = 1                                             # 速度分辨率
        self.dw = 0.01 * math.pi                                # 角度分辨率
        self.dt = 0.01                                          # 时间分辨率
        self.predict_time = 3                                   # 未来预测时间
        self.goal_cost_gain = 1.0                               # 目标代价增益
        self.speed_cost_gain = 1.0                              # 速度代价增益
        self.robot_size = 25                                    # 机器人半径大小


def motion(x, u, dt):
    """
    :param x: 位置参数，表征位置空间
    :param u: 速度参数，表征速度空间
    :param dt: 采样时间
    :return:
    """
    x[0] = x[0] + u[0] * math.cos(x[2]) * dt - u[1] * math.sin(x[2]) * dt               # x
    x[1] = x[1] + u[0] * math.sin(x[2]) * dt + u[1] * math.cos(x[2]) * dt               # y
    x[2] = x[2] + u[2] * dt                                                             # theta
    x[3] = u[0]                                                                         # vx
    x[4] = u[1]                                                                         # vy
    x[5] = u[2]                                                                         # w
    return x


def dynamic_window(x, config):
    """
    :param x: 位置参数，表征位置空间
    :param config: 参数配置集合
    :return: 动态窗口内的速度范围
    """
    v = (x[3] ** 2 + x[4] ** 2) ** 0.5
    vs = [config.min_speed, config.max_speed, config.min_rate, config.max_rate]         # 机器人最大/最小线速度以及角速度
    vd = [v - config.max_acc_speed * config.dt,
          v + config.max_acc_speed * config.dt,
          x[5] - config.max_acc_rate * config.dt,
          x[5] + config.max_acc_rate * config.dt]                                       # 一个采样周期内线/角速度变化范围
    vr = [max(vs[0], vd[0]), min(vs[1], vd[1]), max(vs[2], vd[2]), min(vs[3], vd[3])]   # 求二者的交集，即为动态窗口
    return vr


def cal_trajectory(x_init, vx, vy, w, config):
    """
    预测未来几秒内的轨迹，具体时长在config.predict_time中配置
    :param x_init: 初始位置空间
    :param vx: x线速度
    :param vy: y线速度
    :param w: 角速度
    :param config: 参数配置集合
    :return: 每一次采样更新的轨迹
    """
    x = np.array(x_init)
    trajectory = np.array(x)
    t = 0
    while t <= config.predict_time:
        x = motion(x, [vx, vy, w], config.dt)
        trajectory = np.vstack((trajectory, x))
        t = t + config.dt
    return trajectory


def goal_cost(trajectory, goal, config):
    """
    计算轨迹到目标的代价
    :param trajectory: cal_trajectory()函数计算出的轨迹
    :param goal: 目标点坐标
    :param config: 参数配置集合
    :return: 轨迹到目标的代价
    """
    d_x = goal[0] - trajectory[-1][0]
    d_y = goal[1] - trajectory[-1][1]
    d = (d_x ** 2 + d_y ** 2) ** 0.5
    cost = d * config.goal_cost_gain
    return cost


def obstacle_cost(trajectory, obj, config):
    """
    计算预测轨迹和障碍物的最小距离作为代价
    :param trajectory: cal_trajectory()函数计算出的轨迹
    :param obj: 障碍物坐标
    :param config: 参数配置集合
    :return: 代价，0-无碰撞，inf-碰撞
    """
    min_r = float("inf")                                                            # 初始化为无穷大
    for i in range(0, len(trajectory[:, 1])):
        for j in range(len(obj[:, 0])):
            ox, oy = obj[j, 0], obj[j, 1]
            dx = trajectory[i, 0] - ox
            dy = trajectory[i, 1] - oy
            r = (dx ** 2 + dy ** 2) ** 0.5
            if r <= config.robot_size:
                return float("inf")
            if min_r >= r:
                min_r = r
    return 1 / min_r


def cal_final_input(x, u, vr, config, goal, obj):
    """
    计算采样空间的评价函数，选择最合适的一个作为最终输入
    :param x: 位置参数，表征位置空间
    :param u: 速度参数，表征速度空间
    :param vr: 动态窗口速度范围
    :param config: 参数配置集合
    :param goal: 目标点坐标
    :param obj: 障碍物坐标
    :return:
    """
    x_init = x[:]                                               # 不用x_init = x是因为这样做改变x_init不会影响x
    min_cost = float("inf")
    min_u = u
    best_tra = np.array([x])
    for vx in np.arange(vr[0], vr[1], config.dv):
        for vy in np.arange(vr[0], vr[1], config.dv):
            for w in np.arange(vr[2], vr[3], config.dw):
                trajectory = cal_trajectory(x_init, vx, vy, w, config)
                cost_goal = goal_cost(trajectory, goal, config)
                cost_obstacle = obstacle_cost(trajectory, obj, config)
                speed_cost = config.speed_cost_gain * (config.max_speed - trajectory[-1, 3])
                final_cost = cost_goal + cost_obstacle + speed_cost
                if min_cost >= final_cost:
                    min_cost = final_cost
                    min_u = [vx, vy, w]
                    best_tra = trajectory
    return min_u, best_tra


def dwa_control(x, u, config, goal, obj):
    """
    :param x: 位置参数，表征位置空间
    :param u: 速度参数，表征速度空间
    :param config: 参数配置集合
    :param goal: 目标点坐标
    :param obj: 障碍物坐标
    :return:
    """
    vr = dynamic_window(x, config)
    u, trajectory = cal_final_input(x, u, vr, config, goal, obj)
    return u, trajectory


def plot_arrow(x, y, yaw, length=0.5, width=0.1):
    """
    绘制模拟时的箭头
    :param x: 横坐标
    :param y:纵坐标
    :param yaw: 航向角
    :param length: 长度
    :param width: 宽度
    :return: None
    """
    plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw), head_length=1.5 * width, head_width=width)
    plt.plot(x, y)


def draw_dynamic_search(best_trajectory, x, goal, obj):
    """
    绘制动态搜索过程图
    :param best_trajectory: 最佳轨迹
    :param x: 位置参数，表征位置空间
    :param goal: 目标位置
    :param obj:
    :return:
    """
    plt.cla()
    plt.plot(best_trajectory[:, 0], best_trajectory[:, 1], "-g")
    plt.plot(x[0], x[1], "xr")
    plt.plot(0, 0, "og")
    plt.plot(goal[0], goal[1], "ro")
    plt.plot(obj[:, 0], obj[:, 1], "bs")
    plot_arrow(x[0], x[1], x[2])
    plt.axis("equal")
    plt.grid(True)
    plt.pause(0.01)


def draw_path(trajectory, goal, obj, x):
    plt.cla()
    plt.plot(x[0], x[1], "xr")
    plt.plot(0, 0, "og")
    plt.plot(goal[0], goal[1], "ro")
    plt.plot(obj[:, 0], obj[:, 1], "bs")
    plot_arrow(x[0], x[1], x[2])
    plt.axis("equal")
    plt.grid(True)
    plt.plot(trajectory[:, 0], trajectory[:, 1], 'r')
    plt.show()


def main():
    x = np.array([0.0, 0.0, math.pi / 2.0, 20, 20, 0.0])
    goal = np.array([10, 10])
    # matrix二维矩阵
    ob = np.matrix([[-1, -1],
                    [0, 2],
                    [4.0, 2.0],
                    [5.0, 4.0],
                    [5.0, 5.0],
                    [5.0, 6.0],
                    [5.0, 9.0],
                    [8.0, 9.0],
                    [7.0, 9.0],
                    [12.0, 12.0]
                    ])
    # ob = np.matrix([[0, 2]])
    u = np.array([0.2, 0.0])
    config = Config()
    trajectory = np.array(x)
    for i in range(1000):
        u, best_trajectory = dwa_control(x, u, config, goal, ob)
        x = motion(x, u, config.dt)
        print(x)
        trajectory = np.vstack((trajectory, x))  # store state history
        if show_gif:
            draw_dynamic_search(best_trajectory, x, goal, ob)
        if math.sqrt((x[0] - goal[0]) ** 2 + (x[1] - goal[1]) ** 2) <= config.robot_size:
            print("Goal!!")
            break
    print("Done")
    draw_path(trajectory, goal, ob, x)


if __name__ == '__main__':
    main()
