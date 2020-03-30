import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import sys
from Node import Node

class Broadcast(Node):
    def __init__(self, name, neighbords):
        self.name = name
        self.neighbords = neighbords
    
    def handle(self, source, msg):
        return (msg, self.neighbords)
        #return novas mensagens