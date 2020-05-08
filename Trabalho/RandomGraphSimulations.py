import RandomGraph as rg
import plotGraph as pg
import des
import numpy as np

n = 10
m = 1
scheduleTimeout = 5
collectorTimeout = 5
knowledgeTimeout = 10
iteratorTimeout = 5
distance = 1
seed = 6
loss_probability = 0.9
regenGraphTimeout = 15
deltaValue = 50
terminationTime = 150


Y = list()
Z = list()
X = range(4, 5)

for i in X:
    res = []
    missess = []
    for _ in range(m):
        graph = rg.RandomGraph(i)
        graph.create_graph()
        graph.add_connections()
        nodes = graph.nodes_list()
        edges = graph.edges_dic(distance)
        simulation = des.Sim(nodes, edges, loss_probability, regenGraphTimeout,
             collectorTimeout, knowledgeTimeout, scheduleTimeout, iteratorTimeout, 
             distance, deltaValue, rg.Types.AVERAGE, terminationTime)
        simulation.start()
        res.append(simulation.time)
        missess.append(simulation.missess)
    Y.append(np.average(res))
    Z.append(np.average(missess))

pg.generateRoundsGraph(X, Y)
pg.generateMissessGraph(X, Z)