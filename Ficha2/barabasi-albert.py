#!/usr/bin/python3


import networkx as nx
import matplotlib.pyplot as plt
import random

G = nx.Graph()
arestas = []
tam = 0

def create_graph(num):
	G.clear()
	H = nx.path_graph(num)
	G.add_nodes_from(H)

def create_list(num):
	i = 0
	tam = num
	arestas = []
	while i < num:
		arestas.append((i, 1))

def add_aresta(num1, num2):
	arestas[num1] = (arestas[num1][0], arestas[num1][1] + 1)
	arestas[num2] = (arestas[num2][0], arestas[num2][1] + 1)
	tam += 2

def get_node(num):
	acum = 0
	for x in arestas:
		acum = acum + (x[1] / tam)
		print(x[1])
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

for x in range(1,10):
	create_graph(x)
	create_list(x)
	add_connections(x)

