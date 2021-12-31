# PACA-PYTHON
# Copyright (C) 2020-2021  PACA
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from itertools import combinations
from numpy import setxor1d
from graph_tool import GraphView
from graph_tool.spectral import adjacency
from pyscipopt import Conshdlr, Model, SCIP_RESULT, quicksum
from scipy.sparse import identity

# This solver relies on The SCIP Optimization Suite, version 7 (not included in the VCS repository, obtainable from
# https://scipopt.org/):
#
#   The SCIP Optimization Suite 7.0
#
#   Gerald Gamrath, Daniel Anderson, Ksenia Bestuzheva, Wei-Kun Chen, Leon Eifler, Maxime Gasse, Patrick Gemander,
#   Ambros Gleixner, Leona Gottwald, Katrin Halbig, Gregor Hendel, Christopher Hojny, Thorsten Koch, Pierre Le Bodic,
#   Stephen J. Maher, Frederic Matter, Matthias Miltenberger, Erik Mühmer, Benjamin Müller, Marc Pfetsch,
#   Franziska Schlösser, Felipe Serrano, Yuji Shinano, Christine Tawfik, Stefan Vigerske, Fabian Wegscheider,
#   Dieter Weninger, Jakob Witzig
#
#   Available at Optimization Online <http://www.optimization-online.org/DB_HTML/2020/03/7705.html> and as
#   ZIB-Report 20-10 <http://nbn-resolving.de/urn:nbn:de:0297-zib-78023>, March 2020
#

def _get_cost_in_graph(graph, v, w):
    return 1 if graph.edge(v, w) else -1


def get_p3(graph):
    # Using BA-Spinner Page 9 - Algorithm 2.1
    conflict_triples = []
    for u in graph.iter_vertices():
        for v, w in combinations(graph.get_all_neighbours(u), 2):
            if not graph.edge(v, w):
                conflict_triples.append((v, u, w))
    return conflict_triples


class P3Hdlr(Conshdlr):
    def _update_constraints(self, check_only, sol=None):
        tmp = self.data.graph.copy()

        for u, v in combinations(tmp.iter_vertices(), 2):
            val = self.model.getSolVal(sol, self.data.variables[min(u, v)][max(u, v)])

            # Edge is present and got removed.
            if self.model.isFeasEQ(val, 1.0) and tmp.edge(u, v):
                tmp.remove_edge(tmp.edge(u, v))

            # Edge ist not present and got added.
            if self.model.isFeasEQ(val, 0.0) and not tmp.edge(u, v):
                tmp.add_edge(u, v)

        return self.data.add_p3_constraints(tmp, check_only)

    def conscheck(self, cons, sol, checkintegrality, checklprows, printreason, completely):
        if self._update_constraints(True, sol):
            return {"result": SCIP_RESULT.INFEASIBLE}
        else:
            return {"result": SCIP_RESULT.FEASIBLE}

    def consenfolp(self, cons, nusefulconss, solinfeasible):
        if self._update_constraints(False):
            return {"result": SCIP_RESULT.CONSADDED}
        else:
            return {"result": SCIP_RESULT.FEASIBLE}

    def conslock(self, cons, locktype, nlockspos, nlocksneg):
        # XXX: Should we implement this method?
        pass


class ScipSolver:
    def __init__(self, instance):
        self.instance = instance
        self.graph = GraphView(instance.graph, vfilt=lambda v: bool(v.out_degree()))

        self.variables = None
        self.cat = "Integer"

        self.cons_iterations = 0
        self.all_three_constraints = False

        # Define Problem and solver
        self.prob = Model("cep")
        self.prob.hideOutput()

        p3hdlr = P3Hdlr()
        p3hdlr.data = self
        self.prob.includeConshdlr(p3hdlr, "P3s", "Checks for P3s", enfopriority=-1, chckpriority=-1, eagerfreq=-1, maxprerounds=0, needscons=False)

    def solve(self):
        self._set_up_model()

        self.add_p3_constraints()

        self._add_dist_rule_constraints()

        self._solve()

        return self.instance

    def _set_up_model(self):
        n = self.graph.base.num_vertices()
        self.variables = [[None for _ in range(0, n)] for _ in range(0, n)]
        objective = 0

        for i, j in combinations(self.graph.iter_vertices(), 2):
            u = min(i, j)
            v = max(i, j)

            self.variables[u][v] = self.prob.addVar(f"e{u}.{v}", self.cat, 0, 1)

            cost = _get_cost_in_graph(self.graph, u, v)
            objective += self.variables[u][v] * cost

        self.prob.setObjective(objective)


    def add_p3_constraints(self, graph=None, check_only=False):
        # Adding constraints
        graph = graph or self.graph
        p3s = get_p3(graph)
        if not check_only:
            for i, p3 in enumerate(p3s):
                u, v, w = p3

                x_uv = self.variables[min(u, v)][max(u, v)]
                x_vw = self.variables[min(v, w)][max(v, w)]
                x_uw = self.variables[min(u, w)][max(u, w)]

                self.prob.addCons(x_uv + x_vw - x_uw >= 0, f"i{self.cons_iterations}p{i}c0")
                if self.all_three_constraints:
                    self.prob.addCons(  x_uv - x_vw + x_uw >= 0, f"i{self.cons_iterations}p{i}c1")
                    self.prob.addCons(- x_uv + x_vw + x_uw >= 0, f"i{self.cons_iterations}p{i}c2")
            self.cons_iterations += 1
        return len(p3s)

    def _add_dist_rule_constraints(self):
        # from Bastos et al. 2014: Efficient algorithms for cluster editing, p. 352
        # We calculate the adjacency matrix from the base graph to ensure the indices match
        m = (adjacency(self.graph.base) + identity(self.graph.base.num_vertices())) ** 2
        for i in combinations(self.graph.iter_vertices(), 2):
            if m[i] == 0:
                self.prob.addCons(self.variables[min(i)][max(i)] == 1)

    def _solve(self):
        self.prob.optimize()
        # NOTE: The objective value is NOT the number of edits. To calculate the number of edits
        #       from the objective value, add the number of non-edges in the original graph

        for u, v in combinations(self.graph.iter_vertices(), 2):
            val = self.prob.getVal(self.variables[min(u, v)][max(u, v)])

            # Edge is present and got removed.
            if self.prob.isFeasEQ(val, 1.0) and self.graph.edge(u, v):
                self.instance.removeEdge((u, v))

            # Edge ist not present and got added.
            if self.prob.isFeasEQ(val, 0.0) and not self.graph.edge(u, v):
                self.instance.addEdge((u, v))


def solver(instance):
    instance = ScipSolver(instance).solve()
    return instance
