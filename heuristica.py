# heuristica.py
# Heurística usada pela Gulosa e pelo A*.

VALOR_RECOMPENSA = 10  # quanto vale pegar uma recompensa (mesma unidade do custo do terreno)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def desvio(pos, recompensa, destino):
    # quantos passos a mais eu ando se passar pela recompensa antes de ir pro destino
    return manhattan(pos, recompensa) + manhattan(recompensa, destino) - manhattan(pos, destino)


def heuristica(pos, faltam, destino):
    # distância até o destino + para cada recompensa que falta:
    #   se o desvio é menor que o valor, compensa ir buscar, então soma o desvio
    #   se não, não compensa, então soma o valor que vou perder
    h = manhattan(pos, destino)
    for recompensa in faltam:
        h += min(VALOR_RECOMPENSA, desvio(pos, recompensa, destino))
    return h
