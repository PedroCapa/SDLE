# Trabalho Sistemas Distribuidos em Larga Escala

## des.py

Simulador

## Node.py

Implementação do Algoritmo Push-Sum Protocol

## RandomGraph.py

Geração de um gráfico aleatório

## plotGraph.py

Geração dos gráficos

## RandomGraphSimulations.py

Arrancar o simulador

### Gossip

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        previous: x,
        target: y,
        id: (z, w),
        data: stuff
    }

### IHave

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        src: x,
        target: y,
        id: (z, w)
    }

### Schedule

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        id: (z, w)
    }

### Request

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        previous: x,
        id: (z, w)
    }

### WeHave

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        previous: x,
        info: dic
    }

### Iterator

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
    }

### Collector

    (time, (src, dest, msg))
    msg = {
        type: 'gossip',
        id: (z, w)
    }

## Estruturas

data = {id: data}
info = {nodo: [id]}
target = {id: target}
values = (value, weight)
