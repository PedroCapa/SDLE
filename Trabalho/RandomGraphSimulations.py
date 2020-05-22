import RandomGraph as rg
import plotGraph as pg
import des
import numpy as np
import matplotlib.pyplot as plt
import random


def random_color():
    rgbl = [255, 0, 0]
    random.shuffle(rgbl)
    return tuple(rgbl)


n = 10
m = 1
scheduleTimeout = 5
collectorTimeout = 5
knowledgeTimeout = 10
iteratorTimeout = 15
distance = 1
seed = 6
loss_probability = 1
regenGraphTimeout = 15000
deltaValue = 10
terminationError = 0.01

values = []

Y = list()
Z = list()
X = range(4, 20)
H = list()

for i in X:
    res = []
    missess = []
    exchange = []
    snap = i
    for _ in range(m):
        graph = rg.RandomGraph(i)
        graph.create_graph()
        graph.add_connections()
        nodes = graph.nodes_list()
        edges = graph.edges_dic(distance)
        simulation = des.Sim(nodes, edges, loss_probability, regenGraphTimeout,
                             collectorTimeout, knowledgeTimeout,
                             scheduleTimeout, iteratorTimeout,
                             distance, deltaValue, rg.Types.AVERAGE,
                             terminationError, snap)
        simulation.start()
        des.printNodes(simulation.nodes)
        values.append(simulation.getValues())
        res.append(simulation.time)
        exchange.append(simulation.exchange)
        missess.append(simulation.missess)
    Y.append(np.average(res))
    Z.append(np.average(missess))
    H.append(np.average(exchange))

pg.generateRoundsGraph(X, Y)
pg.generateMissessGraph(X, Z)
pg.generateExchangeGraph(X, H)

snapshot = simulation.snapshot

plt.figure(1)
for key in snapshot.keys():
    if key != 'time':
        plt.plot(snapshot['time'], snapshot[key], "r")

plt.show()

print(values)
