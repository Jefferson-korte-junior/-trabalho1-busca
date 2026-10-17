# algoritmos/profundidade.py
# Busca em profundidade (DFS): pilha LIFO. Busca cega, não olha custo nem recompensa.

from algoritmos.util import reconstruir_caminho


def buscar(mapa, inicio, destino, recompensas):
    pilha = [inicio]
    pai = {inicio: None}
    visitados = set()
    expandidos = []

    while pilha:
        atual = pilha.pop()
        if atual in visitados:
            continue
        visitados.add(atual)
        if atual == destino:
            return reconstruir_caminho(pai, atual), expandidos, len(pai)
        expandidos.append(atual)
        # empilha ao contrário para a primeira direção (cima) sair primeiro
        for vizinho in reversed(mapa.vizinhos(atual)):
            if vizinho not in visitados:
                pai[vizinho] = atual
                pilha.append(vizinho)

    return None, expandidos, len(pai)  # a pilha esvaziou: não existe caminho
