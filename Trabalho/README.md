# Trabalho Sistemas Distribuidos em Larga Escala

## Tarefas

Fazer os handler na classe PushSumProtocol de cada tipo de evento (x)
Acrescentar o evento iterator no simulador (x)
Fazer o método que gera os eventos iniciais (x)
Atribuir os valores iniciais a todos os nodoso (x)
Alterar estrutura do grafo de x em x segundos (x)
Tirar snapshots aos valores do sistema
Caso o target seja nosso vizinho pedir o request (?)
Limpar o dicionario da data ()
Terminar quando o erro for menor que um determinado valor ()
Correr com grafos com vários nodos de forma a ver a influência do tamanho do grafo no tempo que demora a acabar ()

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

### Garbage Collector

Deve ser feito no evento knowledge
Quando souber que o target já tem os dados remover essa entrada do dicionário data

### Tasks

* Review handleKnowledge to just send the greatest id of each node
* Review handleWeHave to add every id beneath the one that received