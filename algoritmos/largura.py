# algoritmos/largura.py
# Busca em largura (BFS): fila FIFO. Busca cega, não olha custo nem recompensa.

from collections import deque

from algoritmos.util import reconstruir_caminho


def buscar(mapa, inicio, destino, recompensas):
    fila = deque([inicio])
    pai = {inicio: None}
    expandidos = []

    while fila:
        atual = fila.popleft()
        if atual == destino:
            return reconstruir_caminho(pai, atual), expandidos, len(pai)
        expandidos.append(atual)
        for vizinho in mapa.vizinhos(atual):
            if vizinho not in pai:
                pai[vizinho] = atual
                fila.append(vizinho)

    return None, expandidos, len(pai)  # a fila esvaziou: não existe caminho
