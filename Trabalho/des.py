import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import sys
from datetime import datetime
from RandomGraph import RandomGraph, Types
from statistics import mean

def printNodes(nodes):
    for node in nodes:
        print('Node: ', node.name, ' Neighbors: ',
          node.neighbors, ' values: ', node.values, 
          ' Data: ', node.data, ' Info: ', node.info, ' Target: ',
          node.target, ' Counter: ', node.counter)

def min_delay(pending):
    min_ = 9223372036854775807
    min_event = pending[0]
    for event in pending:
        if(event[0] < min_):
            min_ = event[0]
            min_event = event
    return min_event

class Sim:
    # nodes é uma lista com os nodos
    # distances é um Map {(0, 1): 100, (1,2): 23} origem, destino e distancia
    def __init__(self, nodes, distances, loss_probability, regenGraphTimeout, 
            collectorTimeout, knowledgeTimeout, scheduleTimeout, iteratorTimeout, 
            distance, deltaValue, type, terminationError, snapTime):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        # [(delay, (src, dst, msg))]
        self.pending = []  # lista de eventos
        # collector time
        self.loss_probability = loss_probability
        # regenerate new graph probability
        self.regenGraphTimeout = regenGraphTimeout
        # number of misses
        self.missess = 0
        # distance between nodes
        self.distance = distance
        self.timeouts = {
            "schedule": scheduleTimeout,
            "collector": collectorTimeout,
            "knowledge": knowledgeTimeout,
            "iterator": iteratorTimeout
        }
        self.deltaValue = deltaValue
        self.type = type
        self.values = []
        self.terminationError = terminationError
        self.snapshot = {}
        self.snapTime = snapTime
        self.exchange = 0

    def getValues(self):
        res = []
        for node in self.nodes:
            res.append(node.getRealValue())
        return res

    def start(self):
        self.assignInitialValues()
        printNodes(self.nodes)
        self.startEvents()
        self.startSnapshot()
        self.run_loop()

    # Function that assigns the initial values to all the nodes
    def assignInitialValues(self):
        # every node should be assigned with (v, 0) but one that is assigned with (u, 1)
        # u, v are random numbers between 0 and deltaValue
        def assignSumValues(self):
            for node in self.nodes:
                randValue = random.random() * self.deltaValue
                node.values = (randValue, 0)
                self.values.append(node.values[0])
            self.nodes[0].setWeight(1)

        def assignAverageValues(self):
            for node in self.nodes:
                randValue = random.random() * self.deltaValue
                node.values = (randValue, 1)
                self.values.append(node.values[0])

        def assignCountValues(self):
            for node in self.nodes:
                node.values = (1, 0)
                self.values.append(node.values[0])
            self.nodes[0].setWeight(1)

        switch = {
            Types.SUM: assignSumValues,
            Types.AVERAGE: assignAverageValues,
            Types.COUNT: assignCountValues
        }
        switch.get(self.type, Types.AVERAGE)(self)
        self.expectedResult = {
            Types.AVERAGE: mean(self.values),
            Types.SUM: sum(self.values),
            Types.COUNT: len(self.nodes)
        }

    def startSnapshot(self):
        self.snapshot['time'] = [0]
        for node in self.nodes:
            self.snapshot[node.name] = [node.getRealValue()]
            
    # the simulator should generate iterators and knowledge events to start the simulation
    def startEvents(self):
        for node in self.nodes:
            self.startPending(node.start(), node.name)
        
    def startPending(self, events, src):
        for (msg, _) in events:
            time = random.randint(0, self.timeouts[msg['type']]) + 1
            self.pending.append((time, (src, src, msg)))

    def only_node_connector(self, node, msg):
        for event in self.pending:
            eventMsg = event[1][2]
            if eventMsg['type'] == "collector" and event[1][1] == node and eventMsg['type'] == msg['id']:
                return False
        return True
    
    def only_node_schedule(self, node, msg):
        for event in self.pending:
            eventMsg = event[1][2]
            if eventMsg['type'] == "schedule" and event[1][1] == node and eventMsg['id'] == msg['id']:
                return False
        return True

    def regenGraph(self, flag):
        if flag and self.time % self.regenGraphTimeout == 0:
            self.genarete_new_graph()
            self.update_pending()

    def genarete_new_graph(self):
        nodes_number = len(self.nodes)
        # generate new graph
        graph = RandomGraph(nodes_number)
        graph.create_graph()
        graph.add_connections()
        # update distances list
        edges = graph.edges_dic(self.distance)
        self.distances = edges
        # change the neighbords of each node
        for node in self.nodes:
            neighbors = list(graph.graph.neighbors(node.name))
            node.neighbors = neighbors

    def update_pending(self):
        for event in self.pending:
            self.remove_event(event)

    def remove_event(self, event):
        event_time = event[0]
        src = event[1][0]
        dst = event[1][1]
        msg = event[1][2]
        type = msg['type']
        if self.trans_event(type) and self.erased_edge(src, dst) and event_time > self.time:
            self.pending.remove(event)

    def trans_event(self, event_type):
        return (event_type == "gossip" or event_type == "ihave"
                or event_type == "request" or event_type == "wehave")

    def erased_edge(self, src, dst):
        return (src, dst) in self.distances

    def generate_events(self, node, message):

        def generateGossip(self, msg, neighbor, node):
            distance = self.distances[(node.name, neighbor)]
            event = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(event)

        def generateIHave(self, msg, neighbor, node):
            distance = self.distances[(node.name, neighbor)]
            lazy = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(lazy)

        def generateSchedule(self, msg, neighbor, node):
            if self.only_node_schedule(neighbor, msg):
                schedule = (self.time + self.timeouts[msg['type']], (node.name, neighbor, msg))
                self.pending.append(schedule)

        def generateRequest(self, msg, neighbor, node):
            distance = self.distances[(node.name, neighbor)]
            request = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(request)

        def generateCollector(self, msg, neighbor, node):
            if self.only_node_connector(neighbor, msg):
                collector = (self.time + self.timeouts[msg['type']], (node.name, neighbor, msg))
                self.pending.append(collector)

        def generateKnowledge(self, msg, neighbor, node):
            knowledge = (self.time + self.timeouts[msg['type']], (node.name, node.name, msg))
            self.pending.append(knowledge)

        def generateWeHave(self, msg, neighbor, node):
            distance = self.distances[(node.name, neighbor)]
            wehave = (self.time + distance, (node.name, neighbor, msg))
            self.pending.append(wehave)

        def generateIterator(self, msg, neighbor, node):
            iterator = (self.time + self.timeouts[msg['type']], (node.name, node.name, msg))
            self.pending.append(iterator)

        switch = {
            "gossip": generateGossip,
            "ihave": generateIHave,
            "schedule": generateSchedule,
            "request": generateRequest,
            "collector": generateCollector,
            "knowledge": generateKnowledge,
            "wehave": generateWeHave,
            "iterator": generateIterator
        }
        events = node.handle(node.name, message)
        for (msg, neighbor) in events:
            switch.get(msg['type'])(self, msg, neighbor, node)

    def canSimulationFinish(self):
        result = self.expectedResult[self.type]
        for node in self.nodes:
            if not node.finish(result, self.terminationError):
                return False
        return True

    def takeSnapshot(self):
        for node in self.nodes:
            self.snapshot[node.name].append(node.getRealValue())

    def simulate_random_loss(self,next_event, probability=1):
        (_, (_, _, msg)) = next_event
        type = msg['type']
        # in case the message has one of the follwing types, there's a chance of loss
        if type == "gossip" or type == "wehave" or type == "ihave" or type == "request":
            self.exchange = self.exchange + 1
            rand = random.uniform(0, 1)
            return rand < probability
        # case its a schedule or collector, the event will allways going to happen
        return True

    def run_loop(self):
        self.time = 1
        snap = 0
        while(not self.canSimulationFinish()):
            # encontrar o evento com o menor delay
            (delay, (src, dst, msg)) = min_delay(self.pending)
            next_event = (delay, (src, dst, msg))
            self.pending.remove(next_event)
            # atualizar o delay de todos os eventos
            regenFlag = (self.time != delay)
            self.time = delay
            # Correr o handle do nodo (return (msg, [id]))
            node = self.nodes[dst]
            if self.simulate_random_loss(next_event, self.loss_probability):
                # Atualizar a lista de eventos
                self.generate_events(node, msg)
            else:
                self.missess = self.missess + 1
            self.regenGraph(regenFlag)

            if delay >= snap + self.snapTime:
                snap = delay
                self.snapshot['time'].append(delay)
                self.takeSnapshot()
