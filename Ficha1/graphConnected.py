#!/usr/bin/python3

import networkx as nx
import matplotlib.pyplot as plt
from random import randrange

G = nx.Graph()

def create_graph(num):
	G.clear()
	H = nx.path_graph(num)
	G.add_nodes_from(H)

def add_connection(num):
	x = randrange(0, num)
	y = randrange(0, num)
	while y == x:
		y = randrange(0, num)
	e = (x, y)
	if not G.has_edge(*e):
		G.add_edge(*e)
	else:
		add_connection(num)

def add_connections(num):
	while not nx.is_connected(G):
		add_connection(num)

def multiple_times(n):
	res = 0
	for i in range(0,n):
		create_graph(n)
		add_connections(n)
		res = res + len(G.edges)
	res = res / n
	return res

n = 10
m = 10
Y = list()
X = range(1, n - 1)

for n in X:
	res = multiple_times(n)
	Y.append(res)
print(Y)