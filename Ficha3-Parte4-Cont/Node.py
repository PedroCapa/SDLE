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
        self.counter = 0
        self.neighbords = neighbords
        self.fanout = fanout
        # payload
        self.data = {}
        # dicionario que contem informação acerca dos vizinhos que receberam
        self.info = {}
        for process in processes:
            self.info[process] = set()


    def getCounterAndIncrement(self):
        self.counter = self.counter + 1
        return self.counter - 1

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

        #Acrescentar o atual e remover todos os inferiores
        self.info[source].add(id)

        #Acrescentar se for superior em 1 unidade ao que temos ou tem indice 0
        flag = False
        contains = False
        for (name, index) in self.info[previous]:
            if name == id[0]:
                contains = True
            if name == id[0] and index == id[1] - 1:
                flag = True
        if flag:
            self.info[previous].remove((id[0], id[1] - 1))
            self.info[previous].add(id)
        elif id[1] == 0 and contains is False:
            self.info[previous].add(id)

        # Verifica se já tem o payload, se já tem ignora mensagem
        if id in self.data.keys():
            return res
        self.data[id] = payload

        # gerar mensagens eager para fanout vizinhos
        rand_nei = self.getRandomNeighbors(previous, id)
        for neighbor in rand_nei:
            message = ("gossip", source, (id, payload))
            res.append((message, neighbor))

        # gerar mensagens lazy para os restantes vizinhos que n tem a informação
        lazy = []
        for neighbor in self.neighbords:
            if neighbor  not in rand_nei:
                flag = True
                for (n,i) in self.info[neighbor]:
                    if n == id[0] and i < id[1]:
                        lazy.append(neighbor)
                    elif n == id[0] and i >= id[1]:
                        flag = False
                if flag:
                    lazy.append(neighbor)

        #lazy = [x for x in self.neighbords if x not in rand_nei and id not in self.info[x]] #Mudar isto
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

        if id not in self.info[source]:
            for neighbor in self.neighbords:
                for (name, index) in self.info[neighbor]:
                    if name == id[0] and index >= id[1]:
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

        flag = False
        contains = False
        for (name, index) in self.info[previous]:
            if name == id[0]:
                contains = True
            if name == id[0] and index == id[1] - 1:
                flag = True
        if flag:
            self.info[previous].remove((id[0], id[1] - 1))
            self.info[previous].add(id)
        elif id[1] == 0 and contains is False:
            self.info[previous].add(id)

        if id not in self.info[source]:
            message = ("schedule", id)
            res.append((message, source))
        return res

    def handleCollector(self, source, msg):
        id = msg[1]
        res = []
        # enviar eager para os vizinhos que não recebeu o ACK
        for neighbor in self.neighbords:
            #if id not in self.info[neighbor]:#Mudar para que verifique se tem o id ou maior
            r = [(name, index) for (name, index) in self.info[neighbor] if name == id[0] and index >= id[1]]

            if len(r) is 0:
                message = ("ihave", source, id)
                res.append((message, neighbor))

        if len(res) > 0:
            message = ("collector", id)
            res.append((message, source))
        return res

    def getRandomNeighbors(self, src, id):
        aux = list(self.neighbords)
        for neighbor in self.neighbords:
            for (name, index) in self.info[neighbor]:#Verificar isto
                if name == id[0] and index >= id[1]:
                    aux.remove(neighbor)

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
        # update the info about the system konwledge
        self.update_system_info(new_info)
        return res

    def update_system_info(self, new_info):
        delete = set()
        for (key, value) in new_info.items():
            for (name, index)  in value:
                delete = [(n,i) for (n,i) in self.info[key] if name == n and i < index and key != self.name]
                
                for d in delete:
                    self.info[key].remove(d)
                
                flag = True
                for (n,i) in self.info[key]:
                    if name == n and i >= index:
                        flag = False
                if flag:
                    self.info[key].add((name, index))
        #Percorrer todos e ver se tem maior

    def handleKnowledge(self, source, msg):
        res = []
        
        send = dict(self.info)
        send[source] = set()
        for key in self.info.keys():
            values = [index for (name, index) in self.info[source] if name == key]
            values.sort()
            if len(values) >= 1 and values[0] == 0:
                last = 0
                for val in values[1:]:
                    if val - 1 in values:
                        last = val
                send[source].add((key, last))
    
        for nei in self.neighbords:
            #Mudar para que n enviei tudo mas que mudifique aquilo que ele proprio sabe e enviar apenas o topo
            message = ("wehave", send, source)
            res.append((message, nei))
        
        self.gerbage_collector()
        message = "knowledge"
        res.append((message, source))
        return res

    def gerbage_collector(self):
        for id in self.data.keys():
            flag = True
            for v in self.info.values():
                res = [i for (n, i) in v if n == id[0]]
                res.sort()
                if id[1] not in res or len(res) == 0 or res[-1] < id[1]:
                    flag = False
            if flag:
                del self.data[id]

