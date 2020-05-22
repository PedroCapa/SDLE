import random
from RandomGraph import RandomGraph, Types
from statistics import mean


def printNodes(nodes):
    """
    print the information about all nodes

    Parameters
    ----------
    nodes: list
        list of values that will be printed
    """
    for node in nodes:
        print('Node: ', node.name, ' Neighbors: ',
              node.neighbors, ' values: ', node.values,
              ' Data: ', node.data, ' Info: ', node.info, ' Target: ',
              node.target, ' Counter: ', node.counter)


def min_delay(pending):
    """
    Pick the message with lower time value

    Parameters
    ----------
    pending: list
        list of messages in queue

    Returns
    ----------
    dictionary
        returns the value with lower time value
    """

    min_ = 9223372036854775807
    min_event = pending[0]
    for event in pending:
        if(event[0] < min_):
            min_ = event[0]
            min_event = event
    return min_event


class Sim:
    """
    Class used to implement the simulator

    Attributes
    ----------
    nodes : list
        list of nodes on the simulator
    distances : list
        distance between nodes
    time : list
        actual time of the simulation
    pending : list
        queue with the messages
    loss_probability : float
        the odds in favour of keeping the node
    regenGraphTimeout : int
        time to time the graph is changed
    misses: int
        number of times the message was lost
    distance : int
        the distance between every node
    timeouts : dictionary
        what messages can be send when the timeout is reached
    deltaValue : int
        max value of the node
    type : Type
        type of calcultion made, COUNT, SUM, AVERAGE
    values : list
        initial values of nodes
    terminationError : float
        percentage of error from the ideal result
    snapshot : dictionary
        dictionary with values of the snapshots
    snapTime: int
        interval between snapshots
    exchange : int
        number of messages exchange between nodes
    """
    def __init__(self, nodes, distances, loss_probability, regenGraphTimeout,
                 collectorTimeout, knowledgeTimeout, scheduleTimeout,
                 iteratorTimeout, distance, deltaValue,
                 type, terminationError, snapTime):
        """
        Constructor of Sim

        Parameters
        ----------
        nodes : list
            list of nodes on the simulator
        distances : list
            distance between nodes
        time : list
            actual time of the simulation
        pending : list
            queue with the messages
        loss_probability : float
            the odds in favour of keeping the node
        regenGraphTimeout : int
            time to time the graph is changed
        misses: int
            number of times the message was lost
        distance : int
            the distance between every node
        timeouts : dictionary
            what messages can be send when the timeout is reached
        deltaValue : int
            max value of the node
        type : Type
            type of calcultion made, COUNT, SUM, AVERAGE
        values : list
            initial values of nodes
        terminationError : float
            percentage of error from the ideal result
        snapshot : dictionary
            dictionary with values of the snapshots
        snapTime: int
            interval between snapshots
        exchange : int
            number of messages exchange between nodes
        """
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        # [(delay, (src, dst, msg))]
        self.pending = []  # lista de eventos
        # collector time
        self.loss_probability = loss_probability
        # regenerate new graph probability
        self.regenGraphTimeout = regenGraphTimeout
        # number of misses
        self.missess = 0
        # distance between nodes
        self.distance = distance
        self.timeouts = {
            "schedule": scheduleTimeout,
            "collector": collectorTimeout,
            "knowledge": knowledgeTimeout,
            "iterator": iteratorTimeout
        }
        self.deltaValue = deltaValue
        self.type = type
        self.values = []
        self.terminationError = terminationError
        self.snapshot = {}
        self.snapTime = snapTime
        self.exchange = 0

    def getValues(self):
        """
        Returns the real value of the list of values

        Returns
        ----------
        list
            the real values of the nodes
        """
        res = []
        for node in self.nodes:
            res.append(node.getRealValue())
        return res

    def start(self):
        """
        Starts the simulation
        """
        self.assignInitialValues()
        printNodes(self.nodes)
        self.startEvents()
        self.startSnapshot()
        self.run_loop()

    # Functtion that assigns the initial values to all the nodes
    def assignInitialValues(self):
        """
        Computes the error of the node and tells if the error is low enough
        """
        def assignSumValues(self):
            """
            sum the values of the nodes
            """
            for node in self.nodes:
                randValue = random.random() * self.deltaValue
                node.values = (randValue, 0)
                self.values.append(node.values[0])
            self.nodes[0].setWeight(1)

        def assignAverageValues(self):
            """
            calculate the average values of the nodes
            """
            for node in self.nodes:
                randValue = random.random() * self.deltaValue
                node.values = (randValue, 1)
                self.values.append(node.values[0])

        def assignCountValues(self):
            """
            calculate the count values of the nodes

            """
            for node in self.nodes:
                node.values = (1, 0)
                self.values.append(node.values[0])
            self.nodes[0].setWeight(1)

        switch = {
            Types.SUM: assignSumValues,
            Types.AVERAGE: assignAverageValues,
            Types.COUNT: assignCountValues
        }
        switch.get(self.type, Types.AVERAGE)(self)
        self.expectedResult = {
            Types.AVERAGE: mean(self.values),
            Types.SUM: sum(self.values),
            Types.COUNT: len(self.nodes)
        }

    def startSnapshot(self):
        """
        Method that starts the snapshot
        """
        self.snapshot['time'] = [0]
        for node in self.nodes:
            self.snapshot[node.name] = [node.getRealValue()]

    # the simulator should generate iterators and
    # knowledge events to start the simulation
    def startEvents(self):
        """
        Method that creates the first events

        Parameters
        ----------
        """
        for node in self.nodes:
            self.startPending(node.start(), node.name)

    def startPending(self, events, src):
        """
        generates the initial events for each node

        Parameters
        ----------
        events : list
            list of events that will be added
        src : int
            node that will be added
        """
        for (msg, _) in events:
            time = random.randint(0, self.timeouts[msg['type']]) + 1
            self.pending.append((time, (src, src, msg)))

    def only_node_connector(self, node, msg):
        """
        checks if is the only node collector

        Parameters
        ----------
        node : node
            node that will be checked if already has a collector
        msg : dict
            message id that will be compared

        Returns
        ----------
        boolean
            if already has a collector
        """
        for event in self.pending:
            eventMsg = event[1][2]
            if (eventMsg['type'] == "collector" and event[1][1] == node and
                    eventMsg['type'] == msg['id']):
                return False
        return True

    def only_node_schedule(self, node, msg):
        """
        checks if exists a schedule for that id

        Parameters
        ----------
        node : node
            node that will be checked if already has a collector
        msg : dict
            message id that will be compared

        Returns
        ----------
        boolean
            if already has a schedule
        """
        for event in self.pending:
            eventMsg = event[1][2]
            if (eventMsg['type'] == "schedule" and event[1][1] == node and
                    eventMsg['id'] == msg['id']):
                return False
        return True

    def regenGraph(self, flag):
        """
        checks if is the only node collector

        Parameters
        ----------
        flag : boolean
            change graph structure
        """
        if flag and self.time % self.regenGraphTimeout == 0:
            self.genarete_new_graph()
            self.update_pending()

    def genarete_new_graph(self):
        """
        generates a new graph
        """
        nodes_number = len(self.nodes)
        # generate new graph
        graph = RandomGraph(nodes_number)
        graph.create_graph()
        graph.add_connections()
        # update distances list
        edges = graph.edges_dic(self.distance)
        self.distances = edges
        # change the neighbords of each node
        for node in self.nodes:
            neighbors = list(graph.graph.neighbors(node.name))
            node.neighbors = neighbors

    def update_pending(self):
        """
        every event calls a function that checks if the message will be removed

        Parameters
        ----------
        """
        for event in self.pending:
            self.remove_event(event)

    def remove_event(self, event):
        """
        Checks if the event will be removed

        Parameters
        ----------
        event: dict
            event that will be checked
        """
        event_time = event[0]
        src = event[1][0]
        dst = event[1][1]
        msg = event[1][2]
        type = msg['type']
        if (self.trans_event(type) and self.erased_edge(src, dst) and
                event_time > self.time):
            self.pending.remove(event)

    def trans_event(self, event_type):
        """
        checks if the message is exchanged between nodes

        Parameters
        ----------
        event_type: dict
            event that will be checked if it exchange

        Returns
        ----------
        boolean
            if the event is exchanged
        """
        return (event_type == "gossip" or event_type == "ihave"
                or event_type == "request" or event_type == "wehave")

    def erased_edge(self, src, dst):
        """
        checks if a message will not be send

        Parameters
        ----------
        src: int
            node that is the source of the message
        dest : int
            node that is the destiny of the message

        Returns
        ----------
        boolean
            if still neighboards
        """
        return (src, dst) in self.distances

    def generate_events(self, node, message):
        """
        Generate the events from messages

        Parameters
        ----------
        msg: dictionary
            message sent by one node
        node: int
            the source of the message
        """

        def generateGossip(self, msg, neighbor, node):
            """
            Generate gossip event from gossip message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            distance = self.distances[(node.name, neighbor)]
            event = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(event)

        def generateIHave(self, msg, neighbor, node):
            """
            Generate ihave event from ihave message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            distance = self.distances[(node.name, neighbor)]
            lazy = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(lazy)

        def generateSchedule(self, msg, neighbor, node):
            """
            Generate schedule event from schedule message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            if self.only_node_schedule(neighbor, msg):
                schedule = (self.time + self.timeouts[msg['type']],
                            (node.name, neighbor, msg))
                self.pending.append(schedule)

        def generateRequest(self, msg, neighbor, node):
            """
            Generate request event from request message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            distance = self.distances[(node.name, neighbor)]
            request = (distance + self.time, (node.name, neighbor, msg))
            self.pending.append(request)

        def generateCollector(self, msg, neighbor, node):
            """
            Generate collector event from collector message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            if self.only_node_connector(neighbor, msg):
                collector = (self.time + self.timeouts[msg['type']],
                             (node.name, neighbor, msg))
                self.pending.append(collector)

        def generateKnowledge(self, msg, neighbor, node):
            """
            Generate knowledge event from knowledge message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            knowledge = (self.time + self.timeouts[msg['type']],
                         (node.name, node.name, msg))
            self.pending.append(knowledge)

        def generateWeHave(self, msg, neighbor, node):
            """
            Generate wehave event from wehave message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            distance = self.distances[(node.name, neighbor)]
            wehave = (self.time + distance, (node.name, neighbor, msg))
            self.pending.append(wehave)

        def generateIterator(self, msg, neighbor, node):
            """
            Generate iterator event from iterator message

            Parameters
            ----------
            msg: dictionary
                message sent by one node
            neighbor: int
                the destiny of the message
            node: int
                the source of the message
            """
            iterator = (self.time + self.timeouts[msg['type']],
                        (node.name, node.name, msg))
            self.pending.append(iterator)

        switch = {
            "gossip": generateGossip,
            "ihave": generateIHave,
            "schedule": generateSchedule,
            "request": generateRequest,
            "collector": generateCollector,
            "knowledge": generateKnowledge,
            "wehave": generateWeHave,
            "iterator": generateIterator
        }
        events = node.handle(node.name, message)
        for (msg, neighbor) in events:
            switch.get(msg['type'])(self, msg, neighbor, node)

    def canSimulationFinish(self):
        """
        Check if all nodes error are below the goal

        Returns
        --------
        bool
            if the simulation can or not finish
        """
        result = self.expectedResult[self.type]
        for node in self.nodes:
            if not node.finish(result, self.terminationError):
                return False
        return True

    def takeSnapshot(self):
        """
        Regists the real values of all nodes
        """
        for node in self.nodes:
            self.snapshot[node.name].append(node.getRealValue())

    def simulate_random_loss(self, next_event, probability=1):
        """
        Simulate the random loss of messages
        exchanged between nodes

        Parameters
        ----------
        next_event: (int, (int, int, dictionary))
            the event that should or not be lost
        probability: float
            probability of losing the message

        Returns
        bool
            if the message was or not dropped
        """
        (_, (_, _, msg)) = next_event
        type = msg['type']
        # in case the message has one of the follwing types,
        # there's a chance of loss
        if (type == "gossip" or type == "wehave" or
                type == "ihave" or type == "request"):
            self.exchange = self.exchange + 1
            rand = random.uniform(0, 1)
            return rand < probability
        # case its a schedule or collector,
        # the event will allways going to happen
        return True

    def run_loop(self):
        """
        Run the simulation until all nodes reach an error
        below the terminationError
        """
        self.time = 1
        snap = 0
        while(not self.canSimulationFinish()):
            # encontrar o evento com o menor delay
            (delay, (src, dst, msg)) = min_delay(self.pending)
            next_event = (delay, (src, dst, msg))
            self.pending.remove(next_event)
            # atualizar o delay de todos os eventos
            regenFlag = (self.time != delay)
            self.time = delay
            # Correr o handle do nodo (return (msg, [id]))
            node = self.nodes[dst]
            if self.simulate_random_loss(next_event, self.loss_probability):
                # Atualizar a lista de eventos
                self.generate_events(node, msg)
            else:
                self.missess = self.missess + 1
            self.regenGraph(regenFlag)

            if delay >= snap + self.snapTime:
                snap = delay
                self.snapshot['time'].append(delay)
                self.takeSnapshot()
