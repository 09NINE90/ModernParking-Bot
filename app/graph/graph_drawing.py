import matplotlib.pyplot as plt
import numpy as np


def draw_linear_graph(graph_title, x_label, y_label, return_file, values_x: list, values_y: list, colors: list | None, plot_label: list):
    plt.figure(figsize=(20, 6))
    if colors is None:
        colors = ["b"] * len(values_y)

    for i in range(len(values_y)):
        plt.plot(values_x[0], values_y[i], colors[i],label=plot_label[i])
    plt.style.use('_mpl-gallery')
    plt.title(graph_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.grid()

    plt.savefig(return_file, dpi=200)
    plt.close()


def draw_bar_graph(graph_title, values_x, values_y: list, bar_labels: list, return_file):
    x = np.arange(len(values_x))
    width = 0.5

    plt.figure(figsize=(20,6))
    for i in range(len(values_y)):
        plt.bar(x, values_y[i], width, label=bar_labels[i])


    plt.xticks(x, values_x)
    plt.legend()
    plt.grid(axis="y")
    plt.title(graph_title)

    plt.tight_layout()
    plt.savefig(return_file, dpi=200)
    plt.close()