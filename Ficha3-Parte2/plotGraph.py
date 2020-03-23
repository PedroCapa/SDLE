import matplotlib.pyplot as plt

def generateGraph(X, Y):
    plt.plot(X, Y)
    plt.ylabel('Number of edges')
    plt.xlabel('Number of nodes')
    plt.show()

def generateRoundsGraph(X, Y):
    plt.plot(X, Y)
    plt.ylabel('Number of rounds')
    plt.xlabel('Number of nodes')
    plt.show()