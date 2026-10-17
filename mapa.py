# mapa.py
# Lê o mapa de um arquivo .txt e transforma a grade em um grafo.

PAREDE = "#"

CUSTOS = {
    ".": 1,   # sólido e plano
    "a": 4,   # arenoso
    "r": 10,  # rochoso
    "p": 20,  # pântano
    "A": 1,   # onde o agente começa (chão sólido)
    "P": 1,   # prêmio (chão sólido)
    "$": 1,   # recompensa (chão sólido)
}

# ordem em que os vizinhos são gerados: cima, direita, baixo, esquerda
DIRECOES = [(0, -1), (1, 0), (0, 1), (-1, 0)]


class Mapa:
    def __init__(self, caminho_arquivo):
        with open(caminho_arquivo, encoding="utf-8-sig") as arquivo:
            self.grade = [list(linha.rstrip("\n")) for linha in arquivo if linha.strip()]

        self.altura = len(self.grade)
        self.largura = len(self.grade[0])
        self.inicio = None
        self.premio = None
        self.recompensas = set()

        for y, linha in enumerate(self.grade):
            if len(linha) != self.largura:
                raise ValueError(f"A linha {y} tem tamanho diferente das outras")
            for x, simbolo in enumerate(linha):
                if simbolo != PAREDE and simbolo not in CUSTOS:
                    raise ValueError(f"Símbolo desconhecido '{simbolo}' na posição ({x}, {y})")
                if simbolo == "A":
                    self.inicio = (x, y)
                elif simbolo == "P":
                    self.premio = (x, y)
                elif simbolo == "$":
                    self.recompensas.add((x, y))

        if self.inicio is None or self.premio is None:
            raise ValueError("O mapa precisa ter um A (agente) e um P (prêmio)")
        if len(self.recompensas) < 5:
            raise ValueError("O mapa precisa ter pelo menos 5 recompensas")

        self.grafo = self.montar_grafo()

    def dentro(self, pos):
        x, y = pos
        return 0 <= x < self.largura and 0 <= y < self.altura

    def eh_parede(self, pos):
        x, y = pos
        return self.grade[y][x] == PAREDE

    def custo(self, pos):
        x, y = pos
        return CUSTOS[self.grade[y][x]]

    def montar_grafo(self):
        # cada célula que não é parede vira um vértice;
        # cada par de células vizinhas que não são parede vira uma aresta
        grafo = {}
        for y in range(self.altura):
            for x in range(self.largura):
                if self.eh_parede((x, y)):
                    continue
                vizinhos = []
                for dx, dy in DIRECOES:
                    vizinho = (x + dx, y + dy)
                    if self.dentro(vizinho) and not self.eh_parede(vizinho):
                        vizinhos.append(vizinho)
                grafo[(x, y)] = vizinhos
        return grafo

    def vizinhos(self, pos):
        return self.grafo[pos]

    def num_vertices(self):
        return len(self.grafo)

    def num_arestas(self):
        return sum(len(v) for v in self.grafo.values()) // 2
