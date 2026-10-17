# agente.py
# Faz o agente andar pela rota: soma o custo de cada célula e pega as recompensas.

from heuristica import VALOR_RECOMPENSA


def percorrer(mapa, rota):
    custo = 0
    coletadas = []
    for pos in rota[1:]:  # a primeira posição é onde ele já está, não paga
        custo += mapa.custo(pos)
        if pos in mapa.recompensas and pos not in coletadas:
            coletadas.append(pos)
    custo_liquido = custo - VALOR_RECOMPENSA * len(coletadas)
    return custo, coletadas, custo_liquido
