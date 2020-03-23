import RandomGraph as rg
import plotGraph as pg
import des
import numpy as np

n = 10
m = 10
timeout = 2
distance = 1
seed = 1

Y = list()
X = range(4, n)

for i in X:
    graph = rg.RandomGraph(i)
    graph.create_graph()
    graph.add_connections()
    nodes = graph.nodes_list()
    edges = graph.edges_dic(distance)
    simulation = des.Sim(nodes, edges, timeout, seed)
    simulation.start()
    Y.append(simulation.time)

pg.generateRoundsGraph(X, Y)