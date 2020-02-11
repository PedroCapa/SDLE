import matplotlib.pyplot as plt
import random2 as rand

def generateGraph(X, Y):
    plt.plot(X, Y)
    plt.ylabel('Number of edges')
    plt.xlabel('Number of nodes')
    plt.show()