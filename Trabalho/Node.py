import networkx as nx
import matplotlib.pyplot as plt
import random
from datetime import datetime


class Node:
    def handle(self, source, msg):
        pass


class PushSumProtocol(Node):

    def __init__(self, neighbors, name, values, fanout, processess):
        self.neighbors = neighbors
        self.name = name
        self.info = {}
        self.data = {}
        self.target = {}
        self.values = values
        self.counter = 0
        self.fanout = fanout
        for process in processess:
            self.info[process] = set()

    def setWeight(self, weight):
        value = self.values[0]
        self.values = (value, weight)

    def getRealValue(self):
        if self.values[1] == 0:
            self.realValue = 9223372036854775807
            return self.realValue
        self.realValue = self.values[0] / self.values[1]
        return self.realValue

    def finish(self, result, terminationError):
            return (abs(self.getRealValue() - result) / result < terminationError)

    #src = proprio nodo
    #message = ('gossip', src, target, (id, data))
    def handle(self, source, msg):
        def handleGossip(self, src, msg):
            res = []
            id = msg['id']
            data = msg['data']
            target = msg['target']
            previous = msg['previous']

            #if the target already knows we do nothing
            if id in self.info[target] or id in self.info[source]:
                return res

            #update the info of the previous and ours
            self.data[id] = data
            self.info[src].add(id)
            self.info[previous].add(id)
            self.target[id] = target

            #if we are the target we do the math
            if target == src:
                self.values = (self.values[0] + data[0], self.values[1] + data[1])
            
            #if the target are our neighbord send a gossip to him
            elif target in self.neighbors:
                message = {'type': 'gossip', 'previous': self.name, 'target': target, 'id': id, 'data': data}
                res.append((message, target))
                message = {'type': 'collector', 'id': id}
                res.append((message, src))

            #else send a gossip and send multiple WeHave
            else:
                gossip = self.getRandomNeighbors(previous, id)
                ihave = self.getIHaveNeighbors(previous, gossip)
                #Adiciona a lista de mensagens das duas
                res.extend(self.addGossipMessages(gossip, id)) 
                res.extend(self.addIHaveMessages(ihave, id))
                message = {'type': 'collector', 'id': id}
                res.append((message, src))
            
            return res

        def handleIHave(self, src, msg):
            res = []
            id = msg['id']
            target = msg['target']
            previous = msg['previous']
            
            #Add the info
            self.info[previous].add(id)
            self.target[id] = target

            #if we are the the target and we do not have the data
            if target == src and id not in self.info[src]:
                message = {'type': 'request', 'previous': self.name, 'id': id}
                res.append((message, previous))

            #if we are the target and we have the data
            elif target == src:
                return []

            #Add the schedule to ask for the data
            schedule = {'type': 'schedule', 'id': id}
            res.append((schedule, src))

            return res

        def handleSchedule(self, src, msg):
            res = []
            id = msg['id']
            target = self.target[id]

            #If we have the info that the target already has the data
            if id in self.info[target]:
                return []
            #If we are not the target but we have the data
            elif id in self.info[self.name]:
                return []
            
            #Ask for data
            nei = self.neighborKnowsInfo(id)
            if len(nei) > 0:
                request = {'type': 'request', 'previous': self.name, 'id': id}
                res.append((request, nei[0]))

            #Reschedule the schedule
            schedule = {'type': 'schedule', 'id': id}
            res.append((schedule, self.name))

            return res

        def handleRequest(self, src, msg):
            previous = msg['previous']
            id = msg['id']
            res = []
            target = self.target[id]
            # just reply if we don't have the info that the target already has the data
            if id not in self.info[target] and previous in self.neighbors:
                data = self.data[id]
                message = {'type': 'gossip', 'previous': self.name,
                           'target': target, 'id': id, 'data': data}
                res.append((message, previous))
            return res

        def handleKnowledge(self, src, msg):
            mat = self.infoToMatrix()
            res = []
            # send to all the neighbors info
            for neighbor in self.neighbors:
                message = {'type': 'wehave', 'previous': self.name, 'info': mat}
                res.append((message, neighbor))
            # if target already received the data remove from data dictionary
            aux = self.data.copy()
            for (id, _) in aux.items():
                dataTarget = self.target[id]
                if id in self.info[dataTarget]:
                    del self.data[id]

            message = {'type': 'knowledge'}
            res.append((message, src))
            return res

        def handleWeHave(self, src, msg):
            new_info = self.matrixToInfo(msg['info'])
            res = []

            for (key, value) in new_info.items():
                self.info[key] = value.union(self.info[key])

            return res

        def handleIterator(self, src, msg):
            res = []
            # create a new iterator
            message = {'type': 'iterator'}
            res.append((message, source))
            # if weight is above 0 send a gossip and collector
            # add to data, to my info and to target and update counter
            if self.values[1] > 0:
                id = self.updateLocal()
                gossipNeighbors = [self.target[id]]
                aux = self.addGossipMessages(gossipNeighbors, id)
                res.extend(aux)
                ihaveNeighbors = self.getIHaveNeighbors(-1, gossipNeighbors)
                aux = self.addIHaveMessages(ihaveNeighbors, id)
                res.extend(aux)
                message = {'type': 'collector', 'id': id}
                res.append((message, src))
            return res

        def handleCollector(self, src, msg):
            res = []
            id = msg['id']
            target = self.target[id]
            
            if id in self.info[target]:
                return res
            
            elif target in self.neighbors and id not in self.info[target]:
                gossipNeighbors = [self.target[id]]
                gossip = self.addGossipMessages(gossipNeighbors, id)

                ihaveNeighbors = self.getIHaveNeighbors(-1, gossipNeighbors)
                ihave = self.addIHaveMessages(ihaveNeighbors, id)
                res = gossip + ihave
                
                message = {'type': 'collector', 'id': id}
                res.append((message, src))

            elif target not in self.neighbors:
                ihaveNeighbors = self.getIHaveNeighbors(-1, [])
                res = self.addIHaveMessages(ihaveNeighbors, id)

            return res

        switch = {
            "gossip": handleGossip,
            "ihave": handleIHave,
            "schedule": handleSchedule,
            "request": handleRequest,
            "knowledge": handleKnowledge,
            "wehave": handleWeHave,
            "iterator": handleIterator,
            "collector": handleCollector,
        }
        return switch.get(msg['type'])(self, source, msg)

    def addIHaveMessages(self, targets, id):
        res = []
        target = self.target[id]
        for tar in targets:
            message = {'type': 'ihave', 'previous': self.name, 'target': target, 'id': id}
            res.append((message, tar))
        return res

    def addGossipMessages(self, targets, id):
        res = []
        target = self.target[id]
        data = self.data[id]
        for tar in targets:
            message = {'type': 'gossip', 'previous': self.name,
                       'target': target, 'id': id, 'data': data}
            res.append((message, tar))
        return res

    def neighborKnowsInfo(self, id):
        return [nei for nei in self.neighbors if id in self.info[nei]]

    def getRandomNeighbors(self, previous, id):
        aux = [x for x in self.neighbors if id not in self.info[x]]
        if previous in aux:
            aux.remove(previous)
        if self.fanout >= len(aux):
            return aux
        return random.sample(aux, self.fanout)

    def getIHaveNeighbors(self, previous, gossip):
        ihave = [x for x in self.neighbors if x not in gossip and x != previous]
        return ihave

    def updateLocal(self):
        id = (self.name, self.counter)
        self.counter = self.counter + 1
        self.values = (self.values[0]/2, self.values[1]/2)
        data = self.values
        target = self.neighbors[random.randint(0, len(self.neighbors) - 1)]
        self.data[id] = data
        self.target[id] = target
        self.info[self.name].add(id)
        return id

    def infoToMatrix(self):
        matrixSize = len(list(self.info.keys()))
        res = [[-1 for col in range(matrixSize)] for row in range(matrixSize)]
        for node in self.info:
            keyIndex = list(self.info.keys()).index(node)
            res[keyIndex] = self.infoToList(node, matrixSize)
        return res

    def infoToList(self, node, matrixSize):
        res = [-1 for elem in range(matrixSize)]
        for (name, id) in self.info[node]:
            nameIndex = list(self.info.keys()).index(name)
            if id > res[nameIndex]:
                res[nameIndex] = id
        res = self.checkList(res, node)
        return res

    def checkList(self, res, node):
        for i in range(len(res)):
            key = list(self.info.keys())[i]
            id = res[i]
            res[i] = self.checkId(key, id, node)
        return res

    def checkId(self, key, id, node):
        while(id > -1):
            idInfo = set([i for (n, i) in self.info[node] if key == n])
            r = set(range(id + 1))
            if r.issubset(idInfo):
                break
            else:
                id = id - 1
        if id == 0 and (key, id) not in self.info[node]:
            id = -1
        return id

    def matrixToInfo(self, matrix):
        newInfo = {}
        matrixSize = len(matrix)
        for i in range(matrixSize):
            key = list(self.info.keys())[i]
            newInfo[key] = self.listToInfo(list(matrix[i]))
        return newInfo

    def listToInfo(self, values):
        res = []
        for i in range(len(values)):
            key = list(self.info.keys())[i]
            value = values[i]
            info = [(key, i) for i in range(value + 1)]
            res.extend(info)
        return set(res)

    def start(self):
        res = []
        message = {'type': 'iterator'}
        res.append((message, self.name))
        message = {'type': 'knowledge'}
        res.append((message, self.name))
        return res

a = PushSumProtocol([1], 3, (0,0), 1, [0,1,2,3])
a.info[0].add((0, 0))
a.info[0].add((0, 1))
a.info[0].add((0, 2))
a.info[0].add((1, 0))
a.info[0].add((1, 1))
a.info[0].add((3, 0))

a.info[1].add((0, 0))
a.info[1].add((1, 0))
a.info[1].add((1,1))
a.info[1].add((1, 2))

a.info[3].add((0, 1))
a.info[3].add((0, 2))
a.info[3].add((1, 0))
a.info[3].add((1, 2))
a.info[3].add((3, 0))
a.info[3].add((3, 1))
mat = a.infoToMatrix()
