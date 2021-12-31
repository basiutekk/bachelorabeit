import networkx as nx


def read_graph(number):
    f = open("./public/memtracker.txt")
    lines = f.readlines()
    vertexCounter = 0
    vertexToLink = {}
    graph = nx.Graph()
    for line in lines[1:]:
        list = line.split(" ")
        vertex1 = list[1]
        vertex2 = list[2]
        v1 = 0
        v2 = 0
        if vertex1 in vertexToLink:
            v1 = vertexToLink[vertex1]
        else:
            vertexToLink[vertex1] = v1 = vertexCounter
            vertexCounter += 1
        if vertex2 in vertexToLink:
            v2 = vertexToLink[vertex2]
        else:
            vertexToLink[vertex2] = v2 = vertexCounter
            vertexCounter += 1
        graph.add_edge(v1,v2)
    print(graph)
    return graph

def write_graph(graph):
    f = open("./public/vc-dafaq.gr","a")
    f.write("p td 960 4888\n")
    for edge in graph.edges():
        f.write(str(edge[0]+1)+" "+str(edge[1]+1)+"\n")
    f.close()







if __name__ == '__main__':
    graph = read_graph(1)
    write_graph(graph)
