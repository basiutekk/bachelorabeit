import loader
import reader


def greedy(graph):
    result = []
    while len(graph.nodes) > 0:
        vertices = list(graph.nodes())
        vertex = vertices[0]
        maxdegree = graph.degree(vertex)
        for v in vertices:
            if graph.degree(v) > maxdegree:
                maxdegree = graph.degree(v)
                vertex = v
        if (maxdegree == 0):
            break
        result.append(vertex)
        graph.remove_node(vertex)
    result.sort()
    print(result)
    print(len(result))

if __name__ == '__main__':
    graphNum = 97
    #graph = loader.paceLoader(graphNum)
    graph = reader.read_graph(1)
    greedy(graph)
