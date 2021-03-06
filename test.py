import numpy as np
from matplotlib import pyplot as plt
BOARD_HEIGHT = 780

a = [[812, 755], [812, 754], [812, 753], [812, 752], [811, 754], [813, 754], [811, 753], [813, 753], [811, 752], [813, 752], [812, 756], [811, 755], [813, 755], [810, 753], [814, 753], [810, 752], [814, 752], [810, 754], [814, 754], [811, 756], [813, 756], [812, 757], [809, 753], [815, 753], [809, 752], [815, 752], [810, 755], [814, 755], [811, 757], [813, 757], [810, 756], [814, 756], [809, 754], [815, 754], [808, 752], [816, 752], [808, 751], [808, 750], [808, 749], [808, 748], [808, 747], [808, 746], [808, 745], [808, 744], [808, 743], [808, 742], [808, 741], [808, 740], [808, 739], [808, 738], [808, 737], [808, 736], [808, 735], [808, 734], [808, 733], [808, 732], [808, 731], [809, 730], [810, 729], [811, 728]]


def show_path(path_list):
    for j in range(len(path_list) - 1):
        x = [path_list[j][0], path_list[j+1][0]]
        y = [BOARD_HEIGHT - 1 - path_list[j][1], BOARD_HEIGHT - 1 - path_list[j+1][1]]
        plt.scatter(x[0], y[0], s=25, marker='.', color='b')
        plt.plot(x, y, 'b--')
    plt.scatter(path_list[len(path_list) - 1][0], BOARD_HEIGHT - 1 - path_list[len(path_list) - 1][1], s=25, marker='.', color='b')
    plt.show()


show_path(a)
