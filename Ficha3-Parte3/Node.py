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
        self.ack = {}
        self.recv = {}

    def handle(self, source, previous, msg):

        if msg[0] == "event":
            res = self.handleEager(source, previous, msg)
        elif msg[0] == "schedule":
            res = self.handleSchedule(source, previous, msg)
        elif msg[0] == "request":
            res = self.handleRequest(source, previous, msg)
        elif msg[0] == "lazy":
            res = self.handleLazy(source, previous, msg)
        elif msg[0] == "collector":
            res = self.handleCollector(source, previous, msg)
        elif msg[0] == "ack":
            res = self.handleAck(source, previous, msg)

        return res

    def add_recv(self, id, previous):
        if id in self.recv:
            self.recv[id].append(previous)
        else:
            self.recv[id] = []
            self.recv[id].append(previous)

    def handleLazy(self, source, previous, msg):
        id = msg[1][0]
        res = []
        self.add_recv(id, previous)
        message = ("ack", (id, source))
        res.append((message, previous))

        if id in self.data.keys():
            return res

        message = ("schedule", (id, source))
        res.append((message, msg[1][1]))
        return res

    def handleSchedule(self, source, previous, msg):
        id = msg[1][0]
        res = []

        if id in self.data.keys():
            return res
        
        message = ("request", (id, source))
        res.append((message, msg[1][1]))
        return res

    def handleEager(self, source, previous, msg):
        res = []
        id = msg[1][0]
        self.add_recv(id, previous)
        rand_nei = self.getRandomNeighbors(previous, id)
        if id in self.data.keys():
            return []

        # gerar mensagens eager para fanout vizinhos
        for neighbor in rand_nei:
            now = datetime.now()
            message = ("event", (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos
        aux = [x for x in self.neighbords if x not in rand_nei]
        aux = [x for x in aux if x not in self.recv[id]]
        lazy = aux.copy()

        if previous in lazy:
            lazy.remove(previous)

        for neighbor in lazy:
            message = ("lazy", (id, source))
            res.append((message, neighbor))

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        message = ("collector", (id, source))
        res.append((message, source))
        self.ack[id] = self.neighbords.copy().remove(previous)
        self.data[id] = msg[1][1]

        message = ("ack", (id, source))
        res.append((message, previous))
        return res

    def handleStartEager(self, source, msg):
        res = []
        rand_nei = self.getRandomNeighborsStart()
        id = msg[1][0]
        if id in self.data.keys():
            return []

        self.ack[id] = self.neighbords.copy()

        # gerar mensagens eager para fanout vizinhos
        for neighbor in rand_nei:
            now = datetime.now()
            message = ("event", (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos
        lazy = [x for x in self.neighbords if x not in rand_nei]
        for neighbor in lazy:
            message = ("lazy", (id, source))
            res.append((message, neighbor))

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        message = ("collector", (id, source))
        res.append((message, source))

        self.data[id] = msg[1][1]
        return res


    def handleRequest(self, source, previous, msg):
        id = msg[1][0]
        res = []
        message = ("event", (id, source))
        res.append((message, msg[1][1]))
        return res

    def handleCollector(self, source, previous, msg):
        id = msg[1][0]
        res = []
        # apagar o conteúdo da mensagem
        if self.ack[id] is None:
            del self.ack[id]
            del self.data[id]
        # enviar eager para os vizinhos que não recebeu o ACK
        else:
            for neighbor in self.ack[id]:
                message = ("event", (id, self.data[id]))
                res.append((message, neighbor))
            message = ("collector", (id, source))
            res.append((message, self.name))
        return res

    def handleAck(self, source, previous, msg):
        id = msg[1][0]
        if (self.ack[id] is not None) and id in self.ack[id]:
            self.ack[id].remove(previous)
        return []

    def getRandomNeighbors(self, src, id):
        aux = [x for x in self.neighbords if x not in self.recv[id]]
        if src in aux:
            aux.remove(src)
        if self.fanout >= len(self.neighbords):
            return aux
        return random.sample(aux, self.fanout)

    def getRandomNeighborsStart(self):
        aux = self.neighbords.copy()
        if self.fanout >= len(self.neighbords):
            return aux
        return random.sample(aux, self.fanout)
