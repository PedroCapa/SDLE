import networkx as nx
import matplotlib.pyplot as plt
import random
from datetime import datetime


class Node:
    def handle(self, source, msg):
        pass


class EagerLazy(Node):
    def __init__(self, name, neighbords, processes, fanout):
        self.name = name
        self.neighbords = neighbords
        self.fanout = fanout
        # payload
        self.data = {}
        # dicionario que contem informação acerca dos vizinhos que receberam
        self.info = {}
        for process in processes:
            self.info[process] = set()
    

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

        self.info[source].add(id)
        self.info[previous].add(id)
        # Verifica se já tem o payload
        if id in self.data.keys():
            return res
        self.data[id] = payload

        # gerar mensagens eager para fanout vizinhos
        rand_nei = self.getRandomNeighbors(previous, id)
        for neighbor in rand_nei:
            message = ("gossip", source, (id, payload))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos
        lazy = [x for x in self.neighbords if x not in rand_nei and id not in self.info[x]]
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
        if id not in self.data.keys() and id not in self.info[source]:
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
        if dest in self.neighbords and id in self.data:
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
        # previous = msg[2]
        # check if the actual node received a new ID
        self.new_id(new_info, res, source)
        # update the info about the system konwledge
        self.update_system_info(new_info)
        # check if the emitter has missing information and still is neighbor
        # for now dont send to the neighbor if contains new information
        # self.send_wehave_previous(previous, new_info, source, res)
        return res

    def send_wehave_previous(self, previous, new_info, source, res):
        if previous in self.neighbords:
            for (key, value) in new_info.items():
                aux = self.info[key] - value
                if aux:
                    message = ("wehave", self.info, source)
                    res.append((message, previous))
                    break

    def new_id(self, new_info, res, source):
        my_ids = set()
        new_ids = set()
        for ids in self.info.values():
            my_ids = my_ids.union(ids)
        for ids in new_info.values():
            new_ids = new_ids.union(ids)
        if new_ids - my_ids:
            message = "knowledge"
            res.append((message, source))

    def update_system_info(self, new_info):
        for (key, value) in new_info.items():
            self.info[key] = value.union(self.info[key])

    def handleKnowledge(self, source, msg):
        res = []
        for nei in self.neighbords:
            message = ("wehave", self.info, source)
            res.append((message, nei))
        
        self.gerbage_collector()
        message = "knowledge"
        res.append((message, source))
        return res

    def gerbage_collector(self):
        flag = True
        key = list(self.info.keys())[0]
        aux = self.info[key].copy()
        for (key, value) in self.info.items():
            aux = aux.intersection(value)
        for id in aux:
            if id in self.data.keys():
                flag = False
                del self.data[id]
        return flag

    def new_knowladge(self, flag, res, source):
        if flag:
            message = "knowledge"
            res.append((message, source))
        else:
            for (key, value) in self.info.items():
                if len(value) > 0 and self.info[key].intersection(set(list(self.data.keys()))):
                    message = "knowledge"
                    res.append((message, source))
                    break
