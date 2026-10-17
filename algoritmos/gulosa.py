# algoritmos/gulosa.py
# Busca gulosa: sempre expande o estado com menor h(n). Não olha o custo já pago.

import heapq

from heuristica import heuristica
from algoritmos.util import FIM, reconstruir_caminho, sucessores, so_posicoes


def buscar(mapa, inicio, destino, recompensas):
    inicial = (inicio, frozenset(recompensas))
    pai = {inicial: None}
    fronteira = [(heuristica(inicio, inicial[1], destino), 0, inicial)]
    contador = 1  # desempate: quem entrou primeiro sai primeiro
    expandidos = []

    while fronteira:
        _, _, estado = heapq.heappop(fronteira)
        if estado == FIM:
            return so_posicoes(reconstruir_caminho(pai, estado)), expandidos, len(pai)
        expandidos.append(estado[0])
        for proximo, _ in sucessores(mapa, estado, destino):
            if proximo not in pai:
                pai[proximo] = estado
                h = 0 if proximo == FIM else heuristica(proximo[0], proximo[1], destino)
                heapq.heappush(fronteira, (h, contador, proximo))
                contador += 1

    return None, expandidos, len(pai)
