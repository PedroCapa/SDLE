import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import sys
import RandomGraph as gc
from datetime import datetime


def min_delay(pending):
    min_ = 9223372036854775807
    min_event = pending[0]
    for event in pending:
        if(event[0] < min_):
            min_ = event[0]
            min_event = event
    return min_event


def simulate_random_loss(next_event, probability = 1):
    (_, (_, _, msg)) = next_event
    type = msg[0]
    # in case the message has one of the follwing types, there's a chance of loss
    if type == "gossip" or type == "ack" or type == "ihave" or type == "request":
        rand = random.uniform(0, 1)
        return rand < probability
    # case its a schedule or collector, the event will allways going to happen
    return True

class Sim:
    # nodes é uma lista com os nodos
    # distances é um Map {(0, 1): 100, (1,2): 23} origem, destino e distancia
    def __init__(self, nodes, distances, timeout, seed, gc_time, probability, know):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        self.timeout = timeout
        self.pending = []  # lista de eventos
        # [(delay, (src, dst, msg))]
        self.seed = seed
        self.gc_time = gc_time
        self.probability = probability
        self.missess = 0
        self.know = know

    def start(self):
        self.start_events()
        for event in self.pending:
            print(event)
        print('-----------------------------------')
        self.run_loop()

    def start_events(self):
        # random root
        size = len(self.nodes)
        for x in range(self.seed):
            key = random.randint(0, size - 1)
            node = self.nodes[key]
            now = datetime.now()
            message = ("gossip", (x, now.strftime("%d/%m/%Y %H:%M:%S")))
            self.generate_start_events(node, message)
        
        self.generate_start_background_events()

    def generate_start_background_events(self):
        for node in self.nodes:
            n = random.randint(2, self.know)
            self.addknowledge(node, n)

    def addknowledge(self, node, n):
        event = (n, (node.name, node.name, "knowledge"))
        self.pending.append(event)


    def only_node_connector(self, node):
        for event in self.pending:
            if event[1][2][0] == "collector" and event[1][1] == node:
                return False
        return True
    
    def only_node_schedule(self, node):
        for event in self.pending:
            if event[1][2][0] == "schedule" and event[1][1] == node:
                return False
        return True

    def update_missess(self, message, events = []):
        if message[0] == "collector":
            self.missess = self.missess + len(events)

    def generate_events(self, node, message):
        events = node.handle(node.name, message)
        self.update_missess(message, events)

        for (msg, neighbor) in events:
            if msg[0] == "schedule":
                if self.only_node_schedule(neighbor):
                    schedule = (self.timeout + self.time, (node.name, neighbor, msg))
                    self.pending.append(schedule)
            elif msg[0] == "gossip":
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            elif msg[0] == "ihave":
                distance = self.distances[(node.name, neighbor)]
                lazy = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(lazy)
            elif msg[0] == "collector":
                if self.only_node_connector(neighbor):
                    collector = (self.time + self.gc_time, (node.name, neighbor, msg))
                    self.pending.append(collector)
            elif msg[0] == "ack":
                distance = self.distances[(node.name, neighbor)]
                ack = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(ack)
            #Em principio so isto
            elif msg == "knowledge":
                knowledge = (self.time + self.know, (node.name, node.name, msg))
                self.pending.append(knowledge)
            elif msg[0] == "wehave":
                distance = self.distances[(node.name, neighbor)]
                wehave = (self.time + distance, (node.name, neighbor, msg))
                self.pending.append(wehave)
            else:
                distance = self.distances[(node.name, neighbor)]
                request = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(request)
            
        for node in self.nodes:
            print(str(node.name) + ": " + str(node.info))
        print('-----------------------------------')
            

    def generate_start_events(self, node, message):
        events = node.handleStartEager(node.name, message)
        for (msg, neighbor) in events:
            if msg[0] == "schedule":
                schedule = (self.timeout + self.time, (node.name, neighbor, msg))
                self.pending.append(schedule)
            elif msg[0] == "gossip":
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            elif msg[0] == "ihave":
                distance = self.distances[(node.name, neighbor)]
                lazy = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(lazy)
            elif msg[0] == "collector":
                if self.only_node_connector(node.name):
                    collector = (self.time + self.gc_time, (node.name, neighbor, msg))
                    self.pending.append(collector)
            elif msg[0] == "ack":
                distance = self.distances[(node.name, neighbor)]
                ack = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(ack)
            else:
                distance = self.distances[(node.name, neighbor)]
                request = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(request)

    def run_loop(self):
        while(len(self.pending) > 0):
            # encontrar o evento com o menor delay
            (delay, (src, dst, msg)) = min_delay(self.pending)
            next_event = (delay, (src, dst, msg))
            self.pending.remove(next_event)
            # atualizar o delay de todos os eventos
            self.time = delay
            # Correr o handle do nodo (return (msg, [id]))
            node = self.nodes[dst]
            for event in self.pending:
                print(event)
            print('-----------------------------------')
            print(next_event)
            if simulate_random_loss(next_event, self.probability):
                # Atualizar a lista de eventos
                print("Mensagem entregue")
                print('-----------------------------------')
                self.generate_events(node, msg)