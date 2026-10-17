# comparativo.py
# Roda os algoritmos no mesmo mapa, mede o tempo e monta as linhas da tabela.

import os
import time

from agente import percorrer
from algoritmos import largura, profundidade, gulosa, a_estrela

ALGORITMOS = {
    "1": ("Largura", largura.buscar),
    "2": ("Profundidade", profundidade.buscar),
    "3": ("Gulosa", gulosa.buscar),
    "4": ("A*", a_estrela.buscar),
}

PASTA = os.path.dirname(os.path.abspath(__file__))
REPETICOES = 20


def rodar(funcao, mapa, inicio, destino, recompensas):
    # roda várias vezes e tira a média, porque uma medida só oscila muito;
    # se passar de meio segundo para antes, pra não travar num mapa grande
    vezes = 0
    comeco = time.perf_counter()
    while True:
        rota, expandidos, na_memoria = funcao(mapa, inicio, destino, recompensas)
        vezes += 1
        gasto = time.perf_counter() - comeco
        if vezes == REPETICOES or gasto > 0.5:
            break
    return rota, expandidos, na_memoria, gasto / vezes * 1000


def calcular(mapa, inicio, destino, recompensas):
    # uma linha da tabela pra cada algoritmo:
    # nome, achou?, custo, passos, recompensas, custo líquido, expandidos, na memória, tempo
    linhas = []
    vistas = {}  # recompensas que apareceram nos vértices visitados pela busca
    for nome, funcao in ALGORITMOS.values():
        rota, expandidos, na_memoria, tempo_ms = rodar(funcao, mapa, inicio, destino, recompensas)
        vistas[nome] = len(set(expandidos) & mapa.recompensas)
        if rota is None:
            linhas.append([nome, "não", "-", "-", "-", "-", len(expandidos), na_memoria, f"{tempo_ms:.2f}"])
        else:
            custo, coletadas, custo_liquido = percorrer(mapa, rota)
            linhas.append([nome, "sim", custo, len(rota) - 1, len(coletadas), custo_liquido,
                           len(expandidos), na_memoria, f"{tempo_ms:.2f}"])
    return linhas, vistas


def grafico(linhas, arquivo=os.path.join(PASTA, "comparativo.png")):
    # salva o gráfico de barras; devolve o caminho do arquivo ou None se não tiver matplotlib
    try:
        import matplotlib
        matplotlib.use("Agg")  # só salva o arquivo, não abre janela
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    nomes = [linha[0] for linha in linhas]
    tempos = [float(linha[8]) for linha in linhas]
    expandidos = [linha[6] for linha in linhas]
    custos = [linha[5] if linha[5] != "-" else 0 for linha in linhas]

    fig, eixos = plt.subplots(1, 3, figsize=(15, 4))
    for eixo, valores, titulo in zip(eixos, [tempos, expandidos, custos],
                                     ["Tempo (ms)", "Nós expandidos", "Custo líquido"]):
        eixo.bar(nomes, valores)
        eixo.set_title(titulo)
        eixo.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(arquivo)
    plt.close(fig)
    return arquivo
