# deteccao.py
# Acha o que o agente alcança, as salas fechadas e os becos sem saída.

from collections import deque


def alcancaveis(mapa, origem):
    # BFS simples a partir do agente: marca tudo que dá pra chegar
    vistos = {origem}
    fila = deque([origem])
    while fila:
        atual = fila.popleft()
        for vizinho in mapa.vizinhos(atual):
            if vizinho not in vistos:
                vistos.add(vizinho)
                fila.append(vizinho)
    return vistos


def salas_fechadas(mapa, origem):
    # células que não são parede mas o agente não alcança, separadas por sala
    chegou = alcancaveis(mapa, origem)
    sobrou = set(mapa.grafo) - chegou
    salas = []
    while sobrou:
        sala = alcancaveis(mapa, sobrou.pop())
        sobrou -= sala
        salas.append(sala)
    return salas


def becos(mapa):
    # beco sem saída: célula com só um vizinho andável
    return [pos for pos, vizinhos in mapa.grafo.items() if len(vizinhos) == 1]
