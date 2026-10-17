# algoritmos/a_estrela.py
# A*: expande o estado com menor f(n) = g(n) + h(n).

import heapq

from heuristica import heuristica
from algoritmos.util import FIM, reconstruir_caminho, sucessores, so_posicoes


def buscar(mapa, inicio, destino, recompensas):
    def h(estado):
        if estado == FIM:
            return 0
        return heuristica(estado[0], estado[1], destino)

    inicial = (inicio, frozenset(recompensas))
    g = {inicial: 0}
    pai = {inicial: None}
    fronteira = [(h(inicial), 0, 0, inicial)]  # (f, desempate, g, estado)
    contador = 1
    expandidos = []

    while fronteira:
        _, _, custo_ate_aqui, estado = heapq.heappop(fronteira)
        if custo_ate_aqui > g[estado]:
            continue  # entrada velha: já achei um caminho mais barato pra esse estado
        if estado == FIM:
            return so_posicoes(reconstruir_caminho(pai, estado)), expandidos, len(g)
        expandidos.append(estado[0])
        for proximo, custo_passo in sucessores(mapa, estado, destino):
            novo_g = custo_ate_aqui + custo_passo
            if novo_g < g.get(proximo, float("inf")):
                g[proximo] = novo_g
                pai[proximo] = estado
                heapq.heappush(fronteira, (novo_g + h(proximo), contador, novo_g, proximo))
                contador += 1

    return None, expandidos, len(g)
