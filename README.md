# Trabalho 1: agente de navegação com busca

Jefferson Korte Junior (2651114) e Igor Carvalho Marchi (2677229)
Fundamentos de Sistemas Inteligentes, prof. Thiago Naves, UTFPR Santa Helena

## Como rodar

Precisa de Python 3 (testamos no 3.14). Dentro da pasta `trabalho1`:

    python interface.py

A janela usa o Tkinter, que já vem com o Python. O gráfico do comparativo usa o matplotlib (`pip install matplotlib`); sem ele o resto funciona normal.
Para conferir todos os algoritmos de uma vez: `python teste_rapido.py`.

## Como usar a janela

A janela mostra o mapa "Escape - Fuga da Prisão": a carinha é o agente, as moedas `$` são as recompensas e a estrela é a saída.

1. Escolha o algoritmo em "Algoritmo" e clique em Executar. A carinha anda pela rota, deixando um rastro laranja e pegando as moedas do caminho. No fim, a caixa "Resultado" mostra o custo, os passos, as recompensas, o custo líquido, os nós expandidos, os nós na memória e o tempo.
2. "Comparar algoritmos" roda todos e mostra a tabela na caixa "Resultado", junto com o tamanho do grafo. Também salva o gráfico `comparativo.png`.
3. "Testar sala sem entrada" coloca o destino dentro da sala fechada do mapa e roda o algoritmo escolhido, para mostrar que ele percebe que não existe caminho. Sempre que não existe caminho, abre uma janelinha de aviso.
4. "Limpar" apaga o desenho da busca e volta o destino para a saída.
5. Para mudar o destino, clique numa casa do mapa. Parar o mouse em cima de uma casa mostra embaixo do mapa a coordenada e o terreno, e avisa quando a casa é beco sem saída ou fica numa sala sem entrada.

![Janela depois de executar o A*](interface.png)

## Organização do código

    trabalho1/
    ├── interface.py             a janela (Tkinter)
    ├── mapa.py                  lê o mapa do .txt e monta o grafo
    ├── heuristica.py            Manhattan, desvio e a heurística da Gulosa e do A*
    ├── agente.py                anda pela rota somando o custo e pegando as recompensas
    ├── deteccao.py              salas fechadas, becos e o que o agente alcança
    ├── comparativo.py           mede tempo e nós e monta a tabela e o gráfico
    ├── teste_rapido.py          confere se as rotas de todos os algoritmos são válidas
    ├── algoritmos/
    │   ├── largura.py           busca em largura (fila)
    │   ├── profundidade.py      busca em profundidade (pilha)
    │   ├── gulosa.py            busca gulosa (fila de prioridade por h)
    │   ├── a_estrela.py         A* (fila de prioridade por g + h)
    │   └── util.py              caminho pelos pais, sucessores e a multa no destino
    └── mapas/
        ├── prisao.txt           mapa da janela, a fuga da prisão (30 x 19)
        ├── mapa1.txt            mapa de teste (20 x 20)
        ├── mapa2_labirinto.txt  labirinto de teste (20 x 15)
        └── mapa3_sem_caminho.txt  teste com o prêmio numa sala sem entrada (15 x 11)

Todos os algoritmos têm a mesma assinatura, `buscar(mapa, inicio, destino, recompensas)`, e devolvem a rota (ou `None` quando não existe caminho), a lista de nós expandidos e quantos estados ficaram guardados na memória. A janela só mostra: quem calcula são os outros módulos. Os três mapas de teste são usados pelo `teste_rapido.py`.

## Como o mapa vira grafo

Cada casa que não é parede é um vértice e cada par de casas vizinhas (cima, baixo, esquerda e direita) é uma aresta. O custo da aresta é o custo do chão da casa para onde o agente vai. O mapa da prisão tem 294 vértices e 359 arestas.

| Símbolo | Significa | Custo para entrar |
|---|---|---|
| `#` | parede | não passa |
| `.` | sólido e plano | 1 |
| `a` | arenoso | 4 |
| `r` | rochoso | 10 |
| `p` | pântano | 20 |
| `A` | início do agente | 1 |
| `P` | saída (prêmio) | 1 |
| `$` | recompensa | 1 |

## A heurística

    h(n) = manhattan(n, destino) + soma, para cada recompensa r que falta, de min(10, desvio(n, r))
    desvio(n, r) = manhattan(n, r) + manhattan(r, destino) - manhattan(n, destino)

O desvio diz quantos passos a mais o agente anda se passar pela recompensa antes de ir ao destino. Para cada recompensa que falta, a heurística soma o menor entre esse desvio e o valor da recompensa (10). Se o desvio é menor que 10, compensa: a cada passo na direção da recompensa o h diminui, então a busca é puxada para ela. Se o desvio é 10 ou mais, o termo fica parado em 10 e a recompensa é ignorada.

Na Gulosa e no A* o estado é (posição, recompensas que faltam), porque estar no mesmo lugar com ou sem uma recompensa pega são situações diferentes. Ao chegar no destino, o agente paga 10 por recompensa que deixou para trás. Usamos multa em vez de desconto para não existir custo negativo, que quebraria o A*. A conta dá no mesmo: o que o A* diminui é o custo do caminho menos 10 por recompensa pega, que chamamos de custo líquido.

A parte da Manhattan é admissível, porque cada passo custa pelo menos 1. A parte das recompensas pode passar do custo real quando duas recompensas estão juntas fora da rota, então a heurística inteira não é admissível e o A* não tem garantia de achar sempre a melhor rota. Nos nossos testes ele achou a melhor rota em todos os mapas.

Exemplo feito à mão: grade 9 x 9 sem paredes, agente em (0, 1), prêmio em (8, 1) e recompensas em (3, 2) e (4, 8). O desvio da primeira é 2 (compensa) e o da segunda é 14 (não compensa), então h = 8 + 2 + 10 = 20. A melhor rota pega só a primeira: 10 passos mais 10 de multa, total 20, igual ao que a heurística previu.

## Recompensas nas buscas cegas

A Largura e a Profundidade não usam as recompensas para decidir nada. Elas pegam as recompensas que estão na rota encontrada (essas entram no custo líquido), e o programa também mostra quantas recompensas apareceram nos vértices visitados durante a busca.

## Detecção de problemas no mapa

- **Sala fechada:** uma busca em largura a partir do agente marca tudo que ele alcança. O que não é parede e ficou sem marca está numa sala sem entrada. A recompensa presa lá fica fora da conta.
- **Beco sem saída:** casa com um vizinho só. O mouse em cima da casa avisa.
- **Sem caminho:** os algoritmos percebem quando a fronteira esvazia sem chegar ao destino, e a tela abre uma janela de aviso. O botão "Testar sala sem entrada" mostra isso.
- **Destino inválido:** clicar em parede ou no ponto onde o agente está é recusado.

## Resultados no mapa da prisão

O tempo é a média de até 20 execuções, só da busca, e muda de computador para computador. Custo líquido é o custo do caminho menos 10 por recompensa pega (quanto menor, melhor).

| Algoritmo | Achou? | Custo | Passos | Recompensas | Custo líquido | Nós expandidos | Nós na memória | Tempo (ms) |
|---|---|---|---|---|---|---|---|---|
| Largura | sim | 120 | 57 | 0 | 120 | 287 | 290 | 0.09 |
| Profundidade | sim | 143 | 65 | 1 | 133 | 73 | 95 | 0.04 |
| Gulosa | sim | 233 | 137 | 4 | 193 | 241 | 280 | 1.02 |
| A* | sim | 112 | 67 | 2 | 92 | 1207 | 1313 | 6.07 |

![Comparativo do mapa da prisão](comparativo.png)

## Conclusões

- A Largura acha o caminho com menos passos (57), mas não o mais barato, porque não olha o custo do terreno.
- A Profundidade acha um caminho qualquer, mais comprido e mais caro.
- A Gulosa é rápida, mas como só olha a estimativa, foi atrás de 4 moedas pagando 233 e ficou com o pior custo líquido.
- O A* teve o melhor custo líquido (92). Ele expande mais nós que os outros porque, além do caminho, decide quais moedas compensa pegar.
- O programa detecta a sala sem entrada, os becos e os destinos sem caminho.
