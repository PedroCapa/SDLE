#!/usr/bin/python3


import networkx as nx
import matplotlib.pyplot as plt
import random

G = nx.Graph()
Y = list()
X = range(1,10)
arestas = []
tam = 0

def create_graph(num):
	G.clear()
	H = nx.path_graph(num)
	G.add_nodes_from(H)

def create_list(num):
	global arestas, tam
	i = 0
	tam = num
	arestas = []
	while i < num:
		arestas.append((i, 1))
		i = i + 1

def add_aresta(num1, num2):
	global tam, arestas
	arestas[num1] = (arestas[num1][0], arestas[num1][1] + 1)
	arestas[num2] = (arestas[num2][0], arestas[num2][1] + 1)
	tam += 2

def get_node(num):
	acum = 0
	for x in arestas:
		acum = acum + (x[1] / tam)
		if acum >= num:
			return x[0]
	return 1

def add_connection(num):
	x = 0
	y = 0
	e = (x, y)
	while x == y or G.has_edge(*e):
		val1 = random.uniform(0, 1)
		val2 = random.uniform(0, 1)
		x = get_node(val1)
		y = get_node(val2)
		e = (x, y)
	G.add_edge(*e)
	add_aresta(x, y)

def add_connections(num):
	while not nx.is_connected(G):
		add_connection(num)

def repeat_multiple_times(number_of_nodes):
	repeat = number_of_nodes - 1
	res = 0
	for x in range(0, repeat):
		create_graph(number_of_nodes)
		create_list(number_of_nodes)
		add_connections(number_of_nodes)
		graph_size = G.number_of_edges()
		res = res + graph_size / repeat
	return res

for x in X:
	res = repeat_multiple_times(x)
	Y.append(res)

def generateGraph(X, Y):
    plt.plot(X, Y)
    plt.ylabel('Number of edges')
    plt.xlabel('Number of nodes')
    plt.show()

generateGraph(X, Y)