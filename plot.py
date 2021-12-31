import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np

graphs = []
results1 = []
results2 = []
results3 = []
results4 = []

def read_result_file():
    f = open("./result/compare_results.txt")
    lines = f.readlines()
    for line in lines[1:]:
        line = line.split(":")
        graph = line[0]
        result_peaty = line[1]
        if result_peaty.__contains__("Nach 30 min abgebrochen"):
            result_peaty=0
        else:
            result_peaty=int(result_peaty)
        result_gnn = line[2]
        result_gnn = int(result_gnn)
        result_lp = line[3]
        result_lp = result_lp.split("(")
        result_lp_upper = result_lp[0]
        result_lp_lower = result_lp[1]
        result_lp_lower = result_lp_lower.split(")")[0]
        result_lp_upper = int(result_lp_upper)
        result_lp_lower = int(result_lp_lower)
        result_greedy = line[4]
        result_greedy = int(result_greedy)
        result_degreedy = line[5]
        result_degreedy = int(result_degreedy)
        write_to_resultfile(graph,result_peaty,result_gnn,result_lp_upper,result_lp_lower,result_greedy,result_degreedy)

def write_to_resultfile(graph,peaty,gnn,lp_upper,lp_lower,greedy,degreedy):
    graphs.append(str(graph))
    gnn_peaty = 0
    peaty_lp = 0
    greedy_peaty = 0
    degreedy_peaty = 0
    if peaty != 0:
        gnn_peaty = gnn/peaty
        peaty_lp = peaty/lp_lower
        greedy_peaty = greedy/peaty
        degreedy_peaty = degreedy/peaty
    results1.append(gnn_peaty)
    results2.append(peaty_lp)
    results3.append(greedy_peaty)
    results4.append(degreedy_peaty)

def plot1(plot_path):
    x = np.arange(25)  # the label locations
    width = 0.2  # the width of the bars
    ymin = 0
    ymax = 2

    fig, ax = plt.subplots()
    ax.bar(x - 1.5 * width, results1[0:25], width, label='Framework/Peaty')
    ax.bar(x - width / 2, results2[0:25], width, label='Peaty/LP')
    ax.bar(x + width / 2, results3[0:25], width, label='Greedy/Peaty')
    ax.bar(x + 1.5 * width, results4[0:25], width, label='DeGreedy/Peaty')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Vergleich der verschiedenen Ergebnisse Graphen 0-24')
    ax.set_ylabel('Value Range')
    ax.set_xlabel('Graph')
    ax.set_xticks(x)
    # ax.set_xticklabels(graphs)
    # Shrink current axis by 15%
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    ax.legend(loc='lower left', )
    ax.set_ylim([ymin, ymax])

    fig.set_size_inches(14, 4)
    fig.savefig(plot_path + 'plot1.png', dpi=100)
    plt.show()

def plot2(plot_path):
        x = np.arange(25,51)  # the label locations
        width = 0.2  # the width of the bars
        ymin = 0
        ymax = 2

        fig, ax = plt.subplots()
        ax.bar(x - 1.5 * width, results1[25:], width, label='Framework/Peaty')
        ax.bar(x - width / 2, results2[25:], width, label='Peaty/LP')
        ax.bar(x + width / 2, results3[25:], width, label='Greedy/Peaty')
        ax.bar(x + 1.5 * width, results4[25:], width, label='DeGreedy/Peaty')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_title('Vergleich der verschiedenen Ergebnisse Graphen 25-50')
        ax.set_ylabel('Value Range')
        ax.set_xlabel('Graph')
        ax.set_xticks(x)
        # ax.set_xticklabels(graphs)
        # Shrink current axis by 15%
        # box = ax.get_position()
        # ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
        ax.legend(loc='lower left', )
        ax.set_ylim([ymin, ymax])

        fig.set_size_inches(14, 4)
        fig.savefig(plot_path + 'plot2.png', dpi=100)
        plt.show()

def plot3(ploth_path):
    x = np.arange(4)  # the label locations
    width = 0.2  # the width of the bars
    ymin = 0.95
    ymax = 1.5
    mean_list = [np.mean(results1),np.mean(results2),np.mean(results3),np.mean(results4)]

    fig, ax = plt.subplots()
    ax.bar(x[0], mean_list[0])
    ax.bar(x[1], mean_list[1])
    ax.bar(x[2], mean_list[2])
    ax.bar(x[3], mean_list[3])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Vergleich der verschiedenen Ergebnisse')
    ax.set_ylabel('Mean Value')
    ax.set_xticks(x)
    solverNames = ["Framework/Peaty","Peaty/LP","Greedy/Peaty","DeGreedy/Peaty"]
    ax.set_xticklabels(solverNames)
    # Shrink current axis by 15%
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    #ax.legend(loc='lower left', )
    ax.set_ylim([ymin, ymax])

    fig.set_size_inches(12,2)
    fig.savefig(plot_path + 'plot3.png', dpi=100)
    plt.show()

if __name__ == '__main__':
    plot_path = "./result/"
    read_result_file()
    plot1(plot_path)
    plot2(plot_path)
    plot3(plot_path)