Inicio (L)

	Boa tarde, o algoritmo que escolhemos foi o Push-Sum Protocol e nesta apresentação vamos falar um pouco sobre ele.

Introdução (L)

	Aqui estão os principais tópicos que vamos falar, que vão desde o motivo pelo qual escolhemos este algoritmo, uma pequena descrição do protocolo, uma explicação da nossa implementação, a exposição do nosso simulador e de que forma este nos ajudou e por fim, a análise de algumas medições que fizemos durante a simulação.

Decisão (P)

	Os motivos pelos quais decidimos escolher o Push-Sum Protocol podem ser reduzidos aos seguintes:
	* Primeiro, este algoritmo funciona para qualquer tipo de topologia, pelo que não nos obrigava a ter particular atenção à construção da rede.
	* Em segundo lugar, este algoritmo em termos da categoria de computação pertence à categoria Average, que tem o princípio de convergir para o resultado correto, que é um principio seguido por muitos algoritmos.
	* Por último, se assegurásemos que uma propriedade fosse cumprida conseguíamos obter o resultado correto.

Protocolo (L)

	Este algoritmo permite o cálculo das funções SUM, COUNT e AVERAGE, através da atribuição de um par de valores a todos os nodos da rede e dependendo dos valores atribuídos é possível calcular uma destas funções de agregação.
	De forma a que todos os nodos calculem o valor das funções da agregação, cada nodo num determinado intervalo de tempo envia metade dos seus valores a um vizinho aleatório e a outra metade fica para si mesmo.
	Quando um nodo recebe uma mensagem de um vizinho, soma os pesos que recebeu na mensagem aos pesos que tinha guardado. 
	Este algoritmo vai ter a tendência para convergir para o resultado correto, quanto maior for o número de mensagens trocadas por entre todos os nodos.
	Uma propriedade que é indispensável manter é a soma dos pesos na rede têm de ser constante de forma a se obter o resultado correto.
	As principais vantagens deste algoritmo consistem no facto de ser fiável, convergir para o resultado correto, os cálculos efetuados em cada nodo serem muito reduzidos e funcionar para qualquer topologia.
	Por outro lado, o tempo para se obter o resultado depende do tamanho e topologia da rede e se houver a falha de um nodo é muito provável que o resultado não convirja.

Implementação (L)

	Inicialmente foi implementado o algoritmo tal como tinha sido descrito em que foi assumido que não ocorreria perda de mensagens e que a topologia era constante.
	Para tal, era apenas necessário criar dois tipos de eventos, um que enviasse os pesos para um vizinho aleatório, o gossip, e um outro evento, o iterator, que em determinados períodos de tempo indicava que um nodo teria que enviar uma mensagem a um vizinho aleatório.
	Como o objetivo de cada gossip passava por enviar os pesos para um nodo vizinho e não para toda a rede, então foi considerado que cada mensagem tinha um target, que não era alterado, mesmo que a mensagem fosse perdida ou a estrutura da rede fosse alterada.

	Para tornar o algoritmo mais completo teríamos de o tornar imune à perda de uma parte das mensagens e à alteração da rede.
	Esta alteração implica que sejam realizadas algumas verificações extra, nomeadamente, sempre que um nodo envie uma mensagem gossip era originado o evento collector.
	Ao fim de um determinado timeout este evento enviava uma mensagem ihave a todos os vizinhos, caso o nodo que originou o gossip não tenha conhecimento que o target tenha recebido a mensagem.

	O nodo que recebia um ihave, originava um evento schedule, que tinha um determinado timeout.
	Passado esse timeout, caso o nodo não soubesse que o target da mensagem já tinha recebido os valores, ia enviar um request a um vizinho que tinha os dados.
	Para que os nodos tivessem conhecimento dos dados recebidos por cada nodo no sistema, criamos o tipo de mensagem wehave que contêm todos os id das mensagens que o próprio nodo conhece e quais os id que sabe que todos os nodos conhecem.
	Desta forma, poderia-se propagar pela rede o conhecimento de cada nodo para eliminar dados de mensagens desnecessárias.
	Estas mensagens eram geradas pelos eventos knowledge em intervalos de tempo fixos.

Simulador (L)

	De forma a verificar a nossa implementação do algoritmo críamos um simulador. 
	No inicio da simulação, o simulador inicializava os pesos dos nodos conforme a função de agregação escolhida.
	Em seguida gerava os eventos iniciais, para posteriormente correr a simulação.

	Na elaboração do simulador decidimos implementar algumas funcionalidades, nomeadamente, a perda de mensagens entre nodos de forma aleatória, a reconstrução da rede em intervalos de tempo fixos, a escolha do timeout de alguns eventos, a escolha da margem de erro para parar a simulação, a contagem do número de mensagens enviadas e perdidas e o suporte para todos os tipos de eventos do protocolo.

	Uma outra funcionalidade que decidimos implementar foram os snapshots, que permitia ao simulador em determinados períodos de tempo obter os valores de cada nodo de forma a verificar se o algoritmo estava com a tendência em convergir e consequentemente, se o algoritmo estava a ser eficaz.

Papel do Simulador (P)

	O simulador que usaríamos para testar o algoritmo ajudou-nos a descobrir algumas falhas na nossa implementação, principalmente na fase de otimização.

	As mensagens que eram enviadas pelos eventos wehave eram dicionários em que a chave era o id de um nodo e o valor é uma lista com os ids das mensagens que o nodo conhece.
	Se em cada evento do tipo wehave fossem enviados estes dicionários, ao fim de algum tempo era causado um grande overhead e muita da informação era repetida.
	Para contornar este problema podíamos transformar a mensagem numa matriz.
	Na primeira implementação o valor era calculado a partir do valor que mais alto de todos os ids de um determinado nodo que tenha todos os número consecutivos a partir do zero.

	Como uma mensagem gossip tem apenas um target, não havia a necessidade de enviar uma mensagem para todos os nodos e com a introdução de otimizações nas mensagens um nodo poderia nunca informar os outros nodos que já tinha uma determinada mensagem.
	Por exemplo, se um nodo recebesse a mensagem com id (0,1), poderia nunca chegar a informar os outros que tinha este id, porque não era obrigatório receber a mensagem com id (0,0), visto que se o target da mensagem com id (0,0) já tivesse recebido a mensagem, esta não ia ser mais propagada pelo resto da rede.
	Ao descobrirmos esta falha modificamos ligeiramente como a otimização era feita.
	Cada valor na matriz, em vez de ser o id máximo, seria a soma dos expoentes de 2 que esse nodo conhecia.

	Por exemplo, se o nodo 0 tivesse os dados das mensagens (1, 1) e (1, 3) o valor na matriz com indices (0,1) seria 10.

	Esta figura mostra o exemplo da transformação de um dicionário para uma matriz.


Resultados (P)

	De forma a confirmar a viabilidade do algoritmo decidimos testar e comparar os resultados de alguns dos valores dos diferentes testes.
	Sempre que utilizamos o programa eram realizadas várias simulações e no fim era feitas as médias do número de mensagens perdidas, enviadas e o tempo que demorou para convergir.
	Além disso, para a última simulação eram registados todos os snapshots para formar um gráfico e ter um representação visual da evolução do peso em cada nodo.

	Este gráfico mostra a evolução dos valores dos pesos dos nodos para a função de agregação COUNT, para um grafo com ligações aleatórias, com probabilidade de perda de mensagens a 0.3 e o erro de terminação de 1%.
	Como podemos ver no final da simulação todos os pesos dos nodos estão próximos do resultado desejado, perto de 30.

	O gráfico da esquerda mostra o tempo médio necessário para convergir, já o da direita mostra o número médio de mensagens trocadas até convergir.
	Como era esperado um maior número de mensagens perdidas representa um aumento no tempo necessário para convergir, principalmente para redes com um número de nodos mais alto, em que uma perda de 30% das mensagens implica uma duplicação do tempo necessário para convergir.
	Já em relação ao número de mensagens enviadas, uma perda de 10% e 30% das mensagens implicou um aumento de 3 e 10 vezes do número de mensagens enviadas, respetivamente.
	Pelo que podemos concluir que a perda de uma mensagem pode implicar o envio de várias mensagens para tentar colmatar a perda.

Conclusão (P)

	Durante esta apresentação fizemos uma exposição de como o Push-Sum Protocol funcionava para o cálculo de funções de agregação, como o simulador implementado nos ajudou a testar o algoritmo e uma análise dos resultado obtidos para diferentes condições de simulação.
	De destacar que os teste feitos poderiam ter sido um pouco mais abrangentes, nomeadamente podiamos ter utilizado topologias diferentes e redes com um número de nodos muito superior.
