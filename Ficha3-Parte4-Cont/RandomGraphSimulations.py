import RandomGraph as rg
import plotGraph as pg
import des
import numpy as np

n = 10
m = 1
timeout = 3
distance = 1
seed = 4
gc_time = 5
loss_probability = 0.9
regenerate_graph_probability = 0.9
know = 10

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
        simulation = des.Sim(nodes, edges, timeout, 
            seed, gc_time, loss_probability, regenerate_graph_probability, know, distance)
        simulation.start()
        res.append(simulation.time)
        missess.append(simulation.missess)
    Y.append(np.average(res))
    Z.append(np.average(missess))

pg.generateRoundsGraph(X, Y)
pg.generateMissessGraph(X, Z)