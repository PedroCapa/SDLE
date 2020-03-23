import networkx as nx
import matplotlib.pyplot as plt
import random
from datetime import datetime


class Node:
    def handle(self, source, msg):
        pass
        # return novas mensagens


class Broadcast(Node):
    def __init__(self, name, neighbords):
        self.name = name
        self.neighbords = neighbords
        self.fanout = 50

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


class EagerLazy(Node):
    def __init__(self, name, neighbords, fanout):
        self.name = name
        self.neighbords = neighbords
        self.fanout = fanout
        self.data = {}

    def handle(self, source, msg):

        if msg[0] == "event":
            res = self.handleEager(source, msg)
        elif msg[0] == "schedule":
            res = self.handleLazy(source, msg)
        elif msg[0] == "request":
            res = self.handleRequest(source, msg)

        return res

    def handleLazy(self, source, msg):
        id = msg[1][0]
        res = []
        if id in self.data.keys():
            return []
        message = ("request", (id, source))
        res.append((message, msg[1][1]))
        return res

    def handleEager(self, source, msg):
        res = []
        rand_nei = self.getRandomNeighbors()
        id = msg[1][0]
        if id in self.data.keys():
            return []

        for neighbor in rand_nei:
            now = datetime.now()
            message = ("event", (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))

        lazy = [x for x in self.neighbords if x not in rand_nei]

        for neighbor in lazy:
            message = ("schedule", (id, source))
            res.append((message, neighbor))

        self.data[id] = msg[1][1]
        return res

    def handleRequest(self, source, msg):
        id = msg[1][0]
        message = ("event", (id, source))
        res = []
        res.append((message, msg[1][1]))
        return res

    def getRandomNeighbors(self):
        if self.fanout >= len(self.neighbords):
            return self.neighbords
        return random.sample(self.neighbords, self.fanout)