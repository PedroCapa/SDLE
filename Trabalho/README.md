# Trabalho Sistemas Distribuidos em Larga Escala

## Tarefas

Fazer os handler na classe PushSumProtocol de cada tipo de evento
Acrescentar o evento iterator no simulador (x)
Fazer o método que gera os eventos iniciais (x)
Atribuir os valores iniciais a todos os nodoso (x)
Alterar estrutura do grafo de x em x segundos (x)
Tirar snapshots aos valores do sistema
Caso o target seja nosso vizinho pedir o request (?)

### Gossip

    (time, (src, dest, msg)) msg->("gossip", src, target, (id, data))
    msg = {
        type: 'gossip',
        previous: x,
        target: y,
        id: (z, w),
        data: stuff
    }

### IHave

    (time, (src, dest, msg)) msg->("ihave", src, target, id)
    msg = {
        type: 'gossip',
        src: x,
        target: y,
        id: (z, w)
    }

### Schedule

    (time, (src, dest, msg)) msg->("schedule", id)
    msg = {
        type: 'gossip',
        id: (z, w)
    }

### Request

    (time, (src, dest, msg)) msg->("request", src, id)
    msg = {
        type: 'gossip',
        previous: x,
        id: (z, w)
    }

### WeHave

    (time, (src, dest, msg)) msg->("wehave", src, info)
    msg = {
        type: 'gossip',
        previous: x,
        info: dic
    }

### Iterator

    (time, (src, dest, msg)) msg->("iterator")
    msg = {
        type: 'gossip',
    }

### Collector

    (time, (src, dest, msg)) msg->("collector", id)
    msg = {
        type: 'gossip',
        id: (z, w)
    }

## Estruturas

data = {id: data}
info = {nodo: [id]}
target = {id: target}
values = (value, weight)
