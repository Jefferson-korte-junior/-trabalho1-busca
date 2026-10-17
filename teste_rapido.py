# teste_rapido.py
# Confere se os algoritmos devolvem rotas válidas em todos os mapas. Rodar com: python teste_rapido.py

import os

from agente import percorrer
from comparativo import ALGORITMOS
from deteccao import alcancaveis
from mapa import Mapa

PASTA_MAPAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapas")


def rota_valida(mapa, rota, inicio, destino):
    if rota[0] != inicio or rota[-1] != destino:
        return False
    for atual, proximo in zip(rota, rota[1:]):
        if proximo not in mapa.vizinhos(atual):  # pulou casa ou entrou em parede
            return False
    return True


for nome_arquivo in sorted(os.listdir(PASTA_MAPAS)):
    mapa = Mapa(os.path.join(PASTA_MAPAS, nome_arquivo))
    chega = alcancaveis(mapa, mapa.inicio)
    recompensas = mapa.recompensas & chega
    print(f"\n{nome_arquivo}: {mapa.num_vertices()} vértices, destino alcançável: {mapa.premio in chega}")
    for nome, funcao in ALGORITMOS.values():
        rota, _, _ = funcao(mapa, mapa.inicio, mapa.premio, recompensas)
        if rota is None:
            assert mapa.premio not in chega, f"{nome} não achou caminho, mas ele existe"
            print(f"  {nome:13} sem caminho (ok)")
            continue
        assert rota_valida(mapa, rota, mapa.inicio, mapa.premio), f"{nome} devolveu rota inválida"
        custo, coletadas, liquido = percorrer(mapa, rota)
        print(f"  {nome:13} ok | custo {custo} | {len(coletadas)} recompensas | custo líquido {liquido}")

print("\nTudo certo.")
