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
    def __init__(self, name, neighbords, processes, fanout):
        self.name = name
        self.neighbords = neighbords
        self.fanout = fanout
        # payload
        self.data = {}
        # dicionario que contem informação acerca dos vizinhos que receberam
        self.info = {}
        for proc in processes:
            self.info[proc] = set()


    def handle(self, source, msg):

        if msg[0] == "gossip":
            res = self.handleGossip(source, msg)
        elif msg[0] == "schedule":
            res = self.handleSchedule(source, msg)
        elif msg[0] == "request":
            res = self.handleRequest(source, msg)
        elif msg[0] == "ihave":
            res = self.handleIHave(source, msg)
        elif msg[0] == "collector":
            res = self.handleCollector(source, msg)
        elif msg[0] == "wehave":
            res = self.handleWehave(source, msg)
        elif msg == "knowledge":
            res = self.handleKnowledge(source, msg)

        return res

    def handleGossip(self, source, msg):
        res = []
        id = msg[2][0]
        previous = msg[1]
        payload = msg[2][1]
        # Verifica se já tem o payload
        if id in self.data.keys():
            return res

        self.info[source].add(id)
        self.info[previous].add(id)
        self.data[id] = payload

        # gerar mensagens eager para fanout vizinhos
        rand_nei = self.getRandomNeighbors(previous, id)
        for neighbor in rand_nei:
            message = ("gossip", source, (id, payload))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos
        # substituir este bocado por uma função, para ser mais percetível
        lazy = [x for x in self.neighbords if x not in rand_nei]

        if previous in lazy:
            lazy.remove(previous)

        for neighbor in lazy:
            message = ("ihave", source, id)
            res.append((message, neighbor))

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        if len(res) > 0:
            message = ("collector", id)
            res.append((message, source))
        return res

    def handleStartEager(self, source, msg):
        res = []
        rand_nei = self.getRandomNeighborsStart()
        id = msg[1][0]
        self.data[id] = msg[1][1]

        self.info[source].add(id)

        # gerar mensagens eager para fanout vizinhos
        for neighbor in rand_nei:
            now = datetime.now()
            message = ("gossip", source, (id, now.strftime("%d/%m/%Y %H:%M:%S")))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos
        lazy = [x for x in self.neighbords if x not in rand_nei]
        for neighbor in lazy:
            message = ("ihave", source, id)
            res.append((message, neighbor))

        # gerar evento GC para verificar se todos ja receberam o conteudo da mensagem
        message = ("collector", id)
        res.append((message, source))
        return res

    def handleSchedule(self, source, msg):
        id = msg[1]
        res = []
        if id not in self.data.keys():
            for neighbor in self.neighbords:
                if id in self.info[neighbor]:
                    message = ("request", source, id)
                    res.append((message, neighbor))
                    break
            message = ("schedule", id)
            res.append((message, source))
        return res

    def handleRequest(self, source, msg):
        id = msg[2]
        dest = msg[1]
        res = []
        message = ("gossip", source, (id, self.data[id]))
        res.append((message, dest))
        return res

    def handleIHave(self, source, msg):
        id = msg[2]
        previous = msg[1]
        res = []
        self.info[previous].add(id)
        if id not in self.data.keys():
            message = ("schedule", id)
            res.append((message, source))
        return res

    def handleCollector(self, source, msg):
        id = msg[1]
        res = []
        # enviar eager para os vizinhos que não recebeu o ACK
        for neighbor in self.neighbords:
            if id not in self.info[neighbor]:
                message = ("ihave", source, id)
                res.append((message, neighbor))
        
        if len(res) > 0:
            message = ("collector", id)
            res.append((message, source))
        return res

    def getRandomNeighbors(self, src, id):
        aux = [x for x in self.neighbords if id not in self.info[x]]
        if src in aux:
            aux.remove(src)
        if self.fanout >= len(aux):
            return aux
        return random.sample(aux, self.fanout)

    def getRandomNeighborsStart(self):
        if self.fanout >= len(self.neighbords):
            return self.neighbords
        return random.sample(self.neighbords, self.fanout)

    def handleWehave(self, source, msg):
        res = []
        new_info = msg[1]
        # Depois responder a um WeHave se tivermos mais informação
        for (key, value) in new_info.items():
            self.info[key] = value.union(self.info[key])

        for (message_id, _) in self.data.items():
            aux = {k:v for (k, v) in self.info.items() if message_id in v}
            if len(aux.keys()) == len(self.info.keys()):
                del self.data[message_id]
                break

        return res

    def handleKnowledge(self, source, msg):
        res = []
        for nei in self.neighbords:
            message = ("wehave", self.info)
            res.append((message, nei))
        # Deixar de enviar knowledge se soubermos tudo
        message = "knowledge"
        res.append((message, ''))
        return res
