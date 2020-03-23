import networkx as nx
import matplotlib.pyplot as plt
import random


class Node:
    def handle(self, source, msg):
        pass
        # return novas mensagens


class Broadcast(Node):
    def __init__(self, name, neighbords):
        self.name = name
        self.neighbords = neighbords

    def handle(self, source, msg):
        res = []
        for neighbor in self.neighbords:
            res.append((msg, neighbor))
        return res
        # return novas mensagens

    def getRandomNeighbors(self):
        if self.fanout >= len(self.neighbords):
            return self.neighbords
        return random.sample(self.neighbords, self.fanout)
