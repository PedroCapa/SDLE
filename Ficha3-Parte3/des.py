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


class Sim:
    # nodes é uma lista com os nodos
    # distances é um Map {(0, 1): 100, (1,2): 23} origem, destino e distancia
    def __init__(self, nodes, distances, timeout, seed, gc_time):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        self.timeout = timeout
        self.pending = []  # lista de eventos
        # [(delay, (src, dst, msg))]
        self.seed = seed
        self.gc_time = gc_time

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
            message = ("event", (x, now.strftime("%d/%m/%Y %H:%M:%S")))
            self.generate_start_events(node, message)

    def only_node_connector(self, node):
        for event in self.pending:
            if event[1][2][0] == "collector" and event[1][1] == node:
                return False
        return True

    def generate_events(self, node, previous, message):
        events = node.handle(node.name, previous, message)
        for (msg, neighbor) in events:
            if msg[0] == "schedule":
                schedule = (self.timeout + self.time, (node.name, neighbor, msg))
                self.pending.append(schedule)
            elif msg[0] == "event":
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            elif msg[0] == "lazy":
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
            else:
                distance = self.distances[(node.name, neighbor)]
                request = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(request)

    def generate_start_events(self, node, message):
        events = node.handleStartEager(node.name, message)
        for (msg, neighbor) in events:
            if msg[0] == "schedule":
                schedule = (self.timeout + self.time, (node.name, neighbor, msg))
                self.pending.append(schedule)
            elif msg[0] == "event":
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            elif msg[0] == "lazy":
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
            # Atualizar a lista de eventos
            self.generate_events(node, src, msg)
            
            for event in self.pending:
                print(event)
            print('-----------------------------------')
