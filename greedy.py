import loader
import reader

def greedy(graph):
    result = []
    while len(graph.nodes) > 0:
        v1 = list(graph)[0]
        if len(list(graph[v1])) > 0:
            v2 = list(graph[v1])[0]
            result.append(v1)
            result.append(v2)
            graph.remove_node(v1)
            graph.remove_node(v2)
        else:
            graph.remove_node(v1)

    print(len(result))

#nimm knoten mit maximalgrad und nimm alle kanten als gecovered.

if __name__ == '__main__':
    graphNum = 97
    #graph = loader.paceLoader(graphNum)
    graph = reader.read_graph(1)
    greedy(graph)
