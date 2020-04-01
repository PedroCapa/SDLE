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
        # payload
        self.data = {}
        # dicionário de nodos que está à espera de receber o ack
        self.ack = {}
        # dicionário de nodos que recebeu o payload
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

    def send_ack(self, id, source, res):
        for recv in self.recv[id]:
            message = ("ack", (id, source))
            res.append((message, recv))
        return res

    def add_recv(self, id, previous):
        if id not in self.recv:
            self.recv[id] = []
            self.recv[id].append(previous)
        elif previous not in self.recv[id]:
            self.recv[id].append(previous)

    def handleLazy(self, source, previous, msg):
        id = msg[1][0]
        res = []
        self.add_recv(id, previous)
        if id not in self.data.keys():
            message = ("schedule", (id, previous))
            res.append((message, source))
        return res

    def handleSchedule(self, source, previous, msg):
        id = msg[1][0]
        res = []
        if id not in self.data.keys():
            message = ("request", (id, source))
            res.append((message, msg[1][1]))
        return res

    def handleEager(self, source, previous, msg):
        res = []
        id = msg[1][0]
        self.add_recv(id, previous)
        res = self.send_ack(id, source, res)
        # enviar um ACK só para garantir que o emissor saiba que recebeu o payload
        if id in self.data.keys():
            return res

        # criar a lista de nodos que está à espera o ACK, se ainda não tiver sido criada
        if id not in self.ack:
            self.ack[id] = []

        # gerar mensagens eager para fanout vizinhos
        rand_nei = self.getRandomNeighbors(previous, id)
        for neighbor in rand_nei:
            now = datetime.now()
            message = ("event", (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))
            self.ack[id].append(neighbor)

        # gerar mensagens lazy para os restantes vizinhos
        # substituir este bocado por uma função, para ser mais percetível
        aux = [x for x in self.neighbords if x not in rand_nei]
        aux = [x for x in aux if x not in self.recv[id]]
        lazy = aux.copy()
        if previous in lazy:
            lazy.remove(previous)

        for neighbor in lazy:
            message = ("lazy", (id, source))
            res.append((message, neighbor))
            self.ack[id].append(neighbor)

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        message = ("collector", (id, previous))
        res.append((message, previous))
        self.data[id] = msg[1][1]
        return res

    def handleStartEager(self, source, msg):
        res = []
        rand_nei = self.getRandomNeighborsStart()
        id = msg[1][0]
        self.ack[id] = []
        self.data[id] = msg[1][1]

        # gerar mensagens eager para fanout vizinhos
        for neighbor in rand_nei:
            now = datetime.now()
            message = ("event", (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))
            self.ack[id].append(neighbor)

        # gerar mensagens lazy para os restantes vizinhos
        lazy = [x for x in self.neighbords if x not in rand_nei]
        for neighbor in lazy:
            message = ("lazy", (id, source))
            res.append((message, neighbor))
            self.ack[id].append(neighbor)

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        message = ("collector", (id, source))
        res.append((message, source))
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
        if (self.ack[id] is None) or len(self.ack[id]) == 0:
            del self.ack[id]
            del self.data[id]
        # enviar eager para os vizinhos que não recebeu o ACK
        else:
            for neighbor in self.ack[id]:
                message = ("event", (id, self.data[id]))
                res.append((message, neighbor))
            message = ("collector", (id, self.name))
            res.append((message, self.name))
        return res

    def handleAck(self, source, previous, msg):
        id = msg[1][0]
        if (id in self.ack) and (self.ack[id] is not None) and (previous in self.ack[id]):
            self.ack[id].remove(previous)
        return []

    def getRandomNeighbors(self, src, id):
        aux = [x for x in self.neighbords if x not in self.recv[id]]
        if src in aux:
            aux.remove(src)
        if self.fanout >= len(aux):
            return aux
        return random.sample(aux, self.fanout)

    def getRandomNeighborsStart(self):
        if self.fanout >= len(self.neighbords):
            return self.neighbords
        return random.sample(self.neighbords, self.fanout)
