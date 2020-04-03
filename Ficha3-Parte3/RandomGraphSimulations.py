import RandomGraph as rg
import plotGraph as pg
import des
import numpy as np

n = 10
m = 10
timeout = 2
distance = 1
seed = 3
gc_time = 3
probability = 0.9

Y = list()
Z = list()
X = range(4, n)

for i in X:
    res = []
    missess = []
    for _ in range(m):
        graph = rg.RandomGraph(i)
        graph.create_graph()
        graph.add_connections()
        nodes = graph.nodes_list()
        edges = graph.edges_dic(distance)
        simulation = des.Sim(nodes, edges, timeout, seed, gc_time, probability)
        simulation.start()
        res.append(simulation.time)
        missess.append(simulation.missess)
    Y.append(np.average(res))
    Z.append(np.average(missess))

pg.generateRoundsGraph(X, Y)
pg.generateMissessGraph(X, Z)