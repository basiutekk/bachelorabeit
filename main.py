from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
import networkx as nx
import loader
import reader


def main(v):
    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Create the variables x and y.
    x = solver.NumVar(0, 1, 'x')
    y = solver.NumVar(0, 2, 'y')

    print('Number of variables =', solver.NumVariables())

    # Create a linear constraint, 0 <= x + y <= 2.
    ct = solver.Constraint(0, 2, 'ct')
    ct.SetCoefficient(x, 1)
    ct.SetCoefficient(y, 1)

    print('Number of constraints =', solver.NumConstraints())

    # Create the objective function, 3 * x + y.
    objective = solver.Objective()
    objective.SetCoefficient(x, 3)
    objective.SetCoefficient(y, 1)
    objective.SetMaximization()

    solver.Solve()

    print('Solution:')
    print('Objective value =', objective.Value())
    print('x =', x.solution_value())
    print('y =', y.solution_value())


def create_var(solverUsed, v):
    return solverUsed.NumVar(0, 1, str(v))


def create_constraint(solverUsed, v1, v2):
    ct = solverUsed.Constraint(1, solverUsed.infinity(), str(v1 + v2))
    ct.SetCoefficient(v1, 1)
    ct.SetCoefficient(v2, 1)


def greedy(graph,tempResult):
    result = tempResult
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
    print(len(result))


if __name__ == '__main__':
    cpp_flags = pywrapinit.CppFlags()
    cpp_flags.logtostderr = True
    cpp_flags.log_prefix = False
    pywrapinit.CppBridge.SetFlags(cpp_flags)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    graphNum = 97
    #graph = loader.paceLoader(graphNum)
    graph = reader.read_graph(1)
    vertices = list(graph.nodes)
    variables = [0 for _ in range(0, graph.number_of_nodes())]
    for v in vertices:
        variables[v] = create_var(solver, v)
    print('Number of variables =', solver.NumVariables())
    solver.Minimize(sum(variables[i] for i in range(0, graph.number_of_nodes())))
    print(len(graph.edges))
    for e in graph.edges:
        create_constraint(solver, variables[e[0]], variables[e[1]])
    print('Number of constraints =', solver.NumConstraints())
    objective = solver.Objective()
    # print(solver.ExportModelAsLpFormat(False))
    solver.Solve()
    print('Solution:')
    print('Objective value =', objective.Value())
    #result = []
    #for x in range(0, len(variables)):
    #    var = variables[x]
    #    print(var.solution_value())
    #    if var.solution_value() > 0.5:
    #        result.append(vertices[x])
    #        graph.remove_node(x)
    #    elif var.solution_value()<0.5:
    #        graph.remove_node(x)
    #print(len(result))
    #print(graph)
    #greedy(graph,result)


