# algoritmos/util.py
# Funções que mais de um algoritmo usa.

from heuristica import VALOR_RECOMPENSA

FIM = "FIM"  # estado final: "o agente parou no destino"


def reconstruir_caminho(pai, fim):
    caminho = []
    atual = fim
    while atual is not None:
        caminho.append(atual)
        atual = pai[atual]
    caminho.reverse()
    return caminho


def sucessores(mapa, estado, destino):
    # Na Gulosa e no A* o estado é (posição, recompensas que faltam pegar).
    pos, faltam = estado
    for vizinho in mapa.vizinhos(pos):
        if vizinho in faltam:
            yield (vizinho, faltam - {vizinho}), mapa.custo(vizinho)
        else:
            yield (vizinho, faltam), mapa.custo(vizinho)
    if pos == destino:
        # parar aqui custa uma multa por recompensa que ficou pra trás
        yield FIM, VALOR_RECOMPENSA * len(faltam)


def so_posicoes(estados):
    # tira o FIM e fica só com a posição de cada estado
    return [estado[0] for estado in estados if estado != FIM]
