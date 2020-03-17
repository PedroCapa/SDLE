import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import sys
import RandomGraph as gc


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
    def __init__(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        self.pending = []  # lista de eventos
        # [(delay, (src, dst, msg))]
        self.visitar = self.full_vis()

    def full_vis(self):
        vis = []
        for node in self.nodes:
            name = node.name
            vis.append(name)
        return vis

    def start(self):
        # random root
        size = len(self.nodes)
        key = random.randint(0, size - 1)
        node = self.nodes[key]
        # remove root from visited list
        self.visitar.remove(key)
        # generate events from root
        self.generate_events(node)
        # run simulator
        self.run_loop()

    def generate_events(self, node):
        events = node.handle(node.name, "xpto")
        for (msg, neighbor) in events:
            distance = self.distances[(node.name, neighbor)]
            event = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(event)

    def run_loop(self):
        while(len(self.pending) > 0 and len(self.visitar) > 0):
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
            self.generate_events(node)
