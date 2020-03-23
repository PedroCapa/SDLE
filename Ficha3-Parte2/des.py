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
    def __init__(self, nodes, distances, timeout, seed):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        self.timeout = timeout
        self.pending = []  # lista de eventos
        # [(delay, (src, dst, msg))]
        self.visitar = self.full_vis()
        self.seed = seed

    def full_vis(self):
        vis = []
        for node in self.nodes:
            name = node.name
            vis.append(name)
        return vis

    def start(self):
        self.start_events()
        self.run_loop()

    def start_events(self):
        # random root
        size = len(self.nodes)
        for x in range(self.seed):
            key = random.randint(0, size - 1)
            node = self.nodes[key]
            now = datetime.now()
            message = ("event", (x, now.strftime("%d/%m/%Y %H:%M:%S")))
            self.generate_events(node, message)

    def generate_events(self, node, message):
        events = node.handle(node.name, message)
        for (msg, neighbor) in events:
            if msg[0] == "schedule":
                event = (self.timeout + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            elif msg[0] == "event":
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)
            else:
                distance = self.distances[(node.name, neighbor)]
                event = (distance + self.time, (node.name, neighbor, msg))
                self.pending.append(event)

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
            if src in self.visitar:
                self.visitar.remove(src)
            # Atualizar a lista de eventos
            self.generate_events(node, msg)
