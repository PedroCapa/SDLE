import networkx as nx
import Node
from random import randrange
from enum import Enum


class Types(Enum):
    """
    Type of aggregation functions
    """
    SUM = 0
    AVERAGE = 1
    COUNT = 2


class RandomGraph:
    """
    Class used to generate a graph with random connections
    between the nodes until it's a completed graph

    Attributes
    ----------
    size: int
        number of nodes
    graph: Graph
        the generated graph
    """
    def __init__(self, size):
        """
        Parameters
        ----------
        size: int
            number of nodes
        """
        self.size = size
        self.graph = nx.Graph()

    def create_graph(self):
        """
        Create a new graph
        """
        H = nx.path_graph(self.size)
        self.graph.add_nodes_from(H)

    def add_connection(self):
        """
        Add connection to the graph between random nodes
        """
        x = randrange(0, self.size)
        y = randrange(0, self.size)
        while y == x:
            y = randrange(0, self.size)
        e = (x, y)
        if not self.graph.has_edge(*e):
            self.graph.add_edge(*e)
        else:
            self.add_connection()

    def add_connections(self):
        """
        Add connections to the graph until it's complete
        """
        while not nx.is_connected(self.graph):
            self.add_connection()

    def multiple_times(self, n):
        """
        Generate some random graphs

        Parameters
        ----------
        n: int
            number of nodes to generate

        Return
        ----------
        float
            the average of connections created
        """
        res = 0
        for _ in range(0, n):
            self.create_graph()
            self.add_connections()
            res = res + len(self.graph.edges)
        res = res / n
        return res

    def edges_dic(self, distance):
        """
        Create a dictionary from the edges of the graph

        Parameters
        ----------
        distance: int
            the value of each connection

        Return
        ----------
        list
            the list of average connections created to each size of graph
        """
        res = {}
        for edge in self.graph.edges:
            res[edge] = distance
            res[tuple((edge[1], edge[0]))] = distance
        return res

    def nodes_list(self):
        """
        Create a list from the nodes of the graph

        Return
        ----------
        list
            list of nodes
        """
        res = []
        for node in self.graph.nodes:
            neighbors = list(self.graph.neighbors(node))
            n = Node.PushSumProtocol(neighbors, node, (0, 0),
                                     1, list(self.graph.nodes))
            res.append(n)
        return res
