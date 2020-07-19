import matplotlib.pyplot as plt


def make_graph_by_args(statistic, filename, suptitle, ox, oy):
    x = [i + 1 for i in range(len(statistic))]
    y = [int(i) for i in statistic][::-1]
    fig = plt.figure()
    plt.plot(x, y)
    fig.suptitle(suptitle)
    plt.xlabel(ox)
    plt.ylabel(oy)
    plt.savefig(filename)
