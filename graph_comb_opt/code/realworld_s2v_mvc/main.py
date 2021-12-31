import parser

import numpy as np
import networkx as nx
import cPickle as cp
import random
import ctypes
import os
import sys
from tqdm import tqdm

sys.path.append('%s/mvc_lib' % os.path.dirname(os.path.realpath(__file__)))
from mvc_lib import MvcLib

sys.path.append('%s/../memetracker' % os.path.dirname(os.path.realpath(__file__)))
from meme import *


def gen_new_graphs(opt, max_n, min_n):
    print ('generating new training graphs')
    sys.stdout.flush()
    api.ClearTrainGraphs()
    for i in tqdm(range(100)):
        while True:
            seed = 1
            cur_n = np.random.randint(max_n - min_n + 1) + min_n
            g = nx.erdos_renyi_graph(n = cur_n, p = 0.5, seed = seed + i)
            assert len(g)
            if len(g) > 300:
                continue
            break
        api.InsertGraph(g, is_test=False)


def greedy(G):
    covered_set = set()
    numCoveredEdges = 0
    idxes = range(nx.number_of_nodes(G))
    idxes = sorted(idxes, key=lambda x: len(list(nx.neighbors(G, x))), reverse=True)
    pos = 0
    while numCoveredEdges < nx.number_of_edges(G):
        new_action = idxes[pos]
        covered_set.add(new_action)
        for neigh in nx.neighbors(G, new_action):
            if neigh not in covered_set:
                numCoveredEdges += 1
        pos += 1
    return len(covered_set)


if __name__ == '__main__':
    api = MvcLib(sys.argv)

    opt = {}
    for i in range(1, len(sys.argv), 2):
        opt[sys.argv[i][1:]] = sys.argv[i + 1]

    g_undirected, _ = build_full_graph('%s/vc-exact_031.gr' % opt['data_root'],'undirected')
    number_of_nodes = nx.number_of_nodes(g_undirected)
    print("Number of Nodes: "+ str(number_of_nodes))
    print(nx.number_of_edges(g_undirected))
    print (greedy(g_undirected))
    max_n = number_of_nodes + 10
    min_n = number_of_nodes - 10
    api.InsertGraph(g_undirected, is_test=True)
    print ("inserted graph!")
    # startup
    gen_new_graphs(opt,max_n,min_n)
    for i in range(10):
        api.lib.PlayGame(100, ctypes.c_double(1.0))
    api.TakeSnapshot()

    eps_start = 1.0
    eps_end = 0.05
    eps_step = 10000.0
    for iter in range(int(opt['max_iter'])):
        if iter and iter % 5000 == 0:
            gen_new_graphs(opt,max_n,min_n)
        eps = eps_end + max(0., (eps_start - eps_end) * (eps_step - iter) / eps_step)
        if iter % 10 == 0:
            api.lib.PlayGame(10, ctypes.c_double(eps))

        if iter % 300 == 0:
            frac = api.lib.Test(0)
            print ('iter', iter, 'eps', eps, 'average pct of vc: ', frac)
            sys.stdout.flush()
            model_path = '%s/iter_%d.model' % (opt['save_dir'], iter)
            api.SaveModel(model_path)

        if iter % 1000 == 0:
            api.TakeSnapshot()

        api.lib.Fit()
