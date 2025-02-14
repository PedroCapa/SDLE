Inicio (L)

	Boa tarde, o algoritmo que escolhemos foi o Push-Sum Protocol e nesta apresentação vamos falar um pouco sobre ele.

Introdução (L)

	Aqui estão os principais tópicos que vamos falar, que vão desde o motivo pelo qual escolhemos este algoritmo à análise de alguns dados que recolhemos durante os testes.

Decisão (P)

	Os motivos pelos quais decidimos escolher o Push-Sum Protocol podem ser reduzidos aos seguintes:
	* Primeiro, este algoritmo funciona para qualquer tipo de topologia, pelo que não nos obrigava a ter especial atenção à construção da rede.
	* Em segundo lugar, este algoritmo em termos da categoria de computação pertence à categoria Average, que tem o princípio de convergir para o resultado correto, que é um principio seguido por muitos algoritmos.
	* Por último, se assegurásemos que uma propriedade fosse cumprida conseguíamos obter o resultado correto.

Protocolo (L)

	O Push-Sum Protocol permite o cálculo das funções SUM, COUNT e AVERAGE, através da atribuição de um par de valores (s, w) a todos os nodos e dependendo dos valores inicialmente atribuídos é possível calcular uma destas funções de agregação.
	O s representa a soma dos valores trocados e o w o peso associado à soma.

	O algoritmo é bastante simples e funciona da seguinte forma:

	Cada nodo num determinado intervalo de tempo envia metade dos seus valores a um vizinho aleatório e a outra metade fica para si mesmo.
	
	Quando um nodo recebe uma mensagem, soma os pesos que recebeu na mensagem aos pesos que tinha guardado. 
	
	Este algoritmo tem a tendência de convergir para o resultado correto, quanto maior for o número de mensagens trocadas.
	
	A soma dos pesos na rede têm de ser constante para que a haja convergência, esta é uma propriedade indispensável.
	
	As principais vantagens deste algoritmo consistem no facto dos cálculos efetuados serem muito reduzidos e funcionar para qualquer topologia.
	
	Por outro lado, o tempo para convergir depende do tamanho e topologia da rede e se houver a falha de um nodo é provável que o resultado não convirja.

Implementação (L)

	Inicialmente implementamos o algoritmo tal como tinha sido descrito em que foi assumido que não haveria perda de mensagens nem troca da estrutura da rede.

	Para tal, era apenas necessário criar dois tipos de eventos, um que enviasse os pesos para um vizinho aleatório, o gossip, e um outro evento, o iterator, que em determinados períodos originava eventos gossip.

	Como o objetivo de cada gossip passava por enviar os pesos para apenas um vizinho e não para toda a rede, então consideradomos que cada mensagem tinha um target, que não era alterado, mesmo que a mensagem fosse perdida ou a estrutura da rede alterada.

	Para tornar o algoritmo mais completo teríamos de o tornar imune à perda de mensagens e à alteração da rede.

	Esta alteração implicou que fosse gerado um evento collector sempre que uma mensagem gossip fosse enviada, que ao fim de um determinado timeout enviava uma mensagem ihave a todos os vizinhos, caso não tenha conhecimento que o target tenha recebido a mensagem.

	O nodo que recebia um ihave, originava um evento schedule, que passado um determinado timeout, caso não soubesse que o target da mensagem já a tinha recebido, ia enviar um request a um vizinho que tinha os dados.

	Para propagar pela rede o conhecimento de cada nodo e criar um garbage collector para eliminar dados desnecessárias criamos os eventos wehave, que consistia no envio dos ids que cada nodo conhecia.

	Estas mensagens eram geradas pelos eventos knowledge em intervalos de tempo fixos.

Simulador (L)

	De forma a verificar a nossa implementação do algoritmo críamos um simulador, que funcionava da seguinte forma:

	Primeiro, os pesos dos nodos eram inicializados conforme a função de agregação escolhida.
	
	Em seguida eram gerados os eventos iniciais, para posteriormente correr a simulação.

	Na elaboração do simulador decidimos implementar algumas funcionalidades, nomeadamente, a perda de mensagens entre nodos de forma aleatória, a reconstrução da rede em intervalos de tempo fixos, a contagem do número de mensagens enviadas e perdidas e o suporte para todos os tipos de eventos do protocolo.

	Uma outra funcionalidade que implementamos foram os snapshots, que permitia ao simulador guardar os valores de cada nodo de forma a verificar se o algoritmo estava com a tendência para convergir.

Papel do Simulador (P)

	O simulador que usamos para testar o algoritmo ajudou-nos a descobrir algumas falhas na nossa implementação, principalmente na fase de otimização.

	As mensagens que eram enviadas pelos eventos wehave eram dicionários em que a chave era o id de um nodo e o valor é uma lista com os ids das mensagens que o nodo conhece.
	Se em cada evento do tipo wehave fossem enviados estes dicionários, iria causar um grande overhead com informação repetida.
	Para contornar este problema podíamos transformar a mensagem numa matriz.
	
	Inicialmente, decidimos que o valor era calculado a partir do valor mais alto de todos os ids de um determinado nodo que tenha todos os números consecutivos a partir do zero.

	Como uma mensagem gossip tem apenas um target, não havia a necessidade de enviar uma mensagem para todos os nodos e com a introdução de otimizações nas mensagens um nodo poderia nunca informar os outros que já tinha uma determinada mensagem.
	Por exemplo, se um nodo recebesse a mensagem com id (0,1), poderia nunca chegar a informar os outros que tinha este id, porque podia não receber a mensagem com id (0,0).
	Ao descobrirmos esta falha modificamos ligeiramente como a otimização era feita.
	Cada valor na matriz seria a soma dos expoentes de 2 que esse nodo conhecia.

	Esta figura mostra o exemplo da transformação de um dicionário para uma matriz.


Resultados (P)

	De forma a confirmar a viabilidade do algoritmo decidimos testar e comparar os resultados de alguns dos valores dos diferentes testes.
	Sempre que utilizamos o programa eram realizadas várias simulações e no fim era feitas as médias do número de mensagens perdidas, enviadas e o tempo que demorou para convergir.
	Além disso, para a última simulação guardamos todos os snapshots para formar um gráfico e ter um representação visual da evolução do peso em cada nodo.

	Este gráfico mostra a evolução dos valores dos pesos dos nodos para a função de agregação COUNT, para um grafo com ligações aleatórias, com probabilidade de perda de mensagens de 0.3 e o erro de terminação de 1% e com 30 nodos.
	Como podemos ver no final da simulação todos os pesos dos nodos estão próximos do resultado desejado, perto de 30.
-------------------------------------------------- Trocar Slide -----------------------------------------------------

	O gráfico da esquerda mostra o tempo médio necessário para convergir, já o da direita mostra o número médio de mensagens trocadas até convergir.
	
	Como era esperado um maior número de mensagens perdidas representa um aumento no tempo necessário para convergir, principalmente para redes com um número de nodos mais alto, em que uma perda de 30% das mensagens implica uma duplicação do tempo necessário para convergir.
	
	Já em relação ao número de mensagens enviadas, uma perda de 10% e 30% das mensagens implicou um aumento de 3 e 10 vezes do número de mensagens enviadas, respetivamente devido ao facto de que a perda de uma mensagem pode implicar o envio de várias para colmatar a perda.

Conclusão (P)

	Durante esta apresentação fizemos uma exposição de como o Push-Sum Protocol funcionava como o simulador implementado nos ajudou a testar o algoritmo e uma análise dos resultado obtidos para diferentes condições de simulação.
	Tal como era previsto, o Push-Sum Protocol consegue obter o resultado correto, no entanto é necessário algum tempo para o obter.
	De destacar que os teste feitos poderiam ter sido um pouco mais abrangentes, nomeadamente podiamos ter utilizado topologias diferentes e redes com um número de nodos muito superior.

