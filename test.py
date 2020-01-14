from matplotlib import pyplot as plt

a = [[10, 10], [10, 16], [10, 22], [10, 28], [14, 28], [14, 24], [14, 20], [14, 16], [14, 12]]
b = [[10, 10], [15, 10], [20, 10], [25, 10], [25, 16], [21, 16], [17, 16], [13, 16], [9, 16]]

for i in range(len(a) - 1):
    x = [a[i][0], a[i][1]]
    y = [a[i + 1][0], a[i + 1][1]]
    plt.scatter(x[0], x[1], marker='.', color='k')
    plt.plot([x[0], y[0]], [x[1], y[1]], 'k--')
plt.scatter(a[len(a) - 1][0], a[len(a) - 1][1], marker='.', color='k')
plt.show()
