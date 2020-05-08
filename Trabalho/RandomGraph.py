import networkx as nx
import matplotlib.pyplot as plt
import Node
from random import randrange
from enum import Enum


class Types(Enum):
    SUM = 0
    AVERAGE = 1
    COUNT = 2


class RandomGraph:
	def __init__(self, size):
		self.size = size
		self.graph = nx.Graph()
	
	def create_graph(self):
		H = nx.path_graph(self.size)
		self.graph.add_nodes_from(H)

	def add_connection(self):
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
		while not nx.is_connected(self.graph):
			self.add_connection()

	def multiple_times(self, n):
		res = 0
		for _ in range(0,n):
			self.create_graph()
			self.add_connections()
			res = res + len(self.graph.edges)
		res = res / n
		return res

	def edges_dic(self, distance):
		res = {}
		for edge in self.graph.edges:
			res[edge] = distance
			res[tuple((edge[1], edge[0]))] = distance
		return res

	def nodes_list(self):
		res = []
		for node in self.graph.nodes:
			neighbors = list(self.graph.neighbors(node))
			n = Node.PushSumProtocol(neighbors, node, (0, 0), 1, list(self.graph.nodes))
			res.append(n)
		return res
