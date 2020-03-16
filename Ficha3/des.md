---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.2'
      jupytext_version: 1.3.4
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import networkx as nx
import matplotlib.pyplot as plt
import random
```

```python
class Sim:
    #nodes é uma lista com os nodos
    #distances é um Map {(0, 1): 100, (1,2): 23} origem, destino e distancia
    def __init__(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.time = 0
        self.pending = [] #lista de eventos
        # [(delay, (src, dst, msg))]
    def start():
        pass

    def min_delay():
        min       = sys.maxint
        min_event = self.pending[0]
        for event in self.pending:
            if(event[0] < min):
                min = event[0]
                min_event = event

    def run_loop():
        while(len(self.pending) > 0):
            # encontrar o evento com o menor delay
            (delay, (src, dst, msg)) = min_delay(self.pending)
            next_event = (delay, (src, dst, msg))
            self.pending.remove(next_event)
            # atualizar o delay de todos os eventos
            self.time = self.time + delay
            # Correr o handle do nodo (return (msg, [id]))
            node = self.nodes[dst]
            (message, dest) = node.handle(src, msg)
            # Atualizar a lista de eventos
            for id in dest:
                distance = self.distances.get(node, id)
                event = (distance + self.time, (node, id, message))
                self.pending.append(event)
```

```python

```
