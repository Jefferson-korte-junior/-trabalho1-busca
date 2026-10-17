# interface.py
# Tela do trabalho feita com Tkinter (já vem com o Python). Rodar com: python interface.py
# A tela só mostra. Quem calcula são os outros módulos (mapa, heurística, algoritmos, agente...).

import math
import os
import tkinter as tk
from tkinter import messagebox, ttk

from agente import percorrer
from comparativo import ALGORITMOS, calcular, grafico, rodar
from deteccao import alcancaveis, becos, salas_fechadas
from mapa import Mapa

ARQUIVO_MAPA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapas", "prisao.txt")
TAM = 24  # tamanho de cada casa em pixels, com o Windows em 100%

CORES = {
    "#": "#4a4a4a",  # parede
    ".": "#d9d9d9",  # sólido e plano
    "A": "#d9d9d9",
    "P": "#d9d9d9",
    "$": "#d9d9d9",
    "a": "#f0dc82",  # arenoso
    "r": "#a0826d",  # rochoso
    "p": "#6c8e5b",  # pântano
}
NOME_TERRENO = {"#": "parede", "a": "arenoso", "r": "rochoso", "p": "pântano"}  # o resto é sólido e plano
OPCOES = [("1", "Busca em Largura"), ("2", "Busca em Profundidade"), ("3", "Busca Gulosa"), ("4", "A*")]
COR_ROTA = "#e67e22"
CINZA = "#808080"
MENSAGEM_INICIAL = "Escolha um algoritmo e clique em Executar."


class Janela:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Trabalho 1 - Escape")
        raiz.resizable(False, False)
        self.tam = round(TAM * raiz.winfo_fpixels("1i") / 96)  # acompanha o zoom do Windows

        self.mapa = Mapa(ARQUIVO_MAPA)
        self.chega = alcancaveis(self.mapa, self.mapa.inicio)
        self.salas = salas_fechadas(self.mapa, self.mapa.inicio)
        self.becos = set(becos(self.mapa))
        self.destino = self.mapa.premio
        self.animacao = None  # id do after() da animação que está rodando

        self.montar_esquerda()
        self.montar_direita()
        self.status = tk.Label(raiz, text=MENSAGEM_INICIAL, anchor="w", relief="sunken", bd=1)
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.atualizar_destino()
        self.desenhar_mapa()

    def montar_esquerda(self):
        esquerda = tk.Frame(self.raiz)
        esquerda.grid(row=0, column=0, sticky="n", padx=(8, 0), pady=(11, 0))
        tk.Label(esquerda, text="Escape - Fuga da Prisão", font=("Arial", 12, "bold")).pack(anchor="w")

        largura = self.mapa.largura * self.tam + 1
        altura = self.mapa.altura * self.tam + 1
        self.tela = tk.Canvas(esquerda, width=largura, height=altura, highlightthickness=0)
        self.tela.pack(pady=(6, 0))
        self.tela.bind("<Motion>", self.mouse_em_cima)
        self.tela.bind("<Button-1>", self.clicou_no_mapa)

        self.info = tk.Label(esquerda, text="", fg=CINZA)
        self.info.pack(anchor="w", pady=(8, 0))

        legenda = tk.Frame(esquerda)
        legenda.pack(anchor="w", pady=(3, 0))
        for simbolo, texto in (("#", "Parede"), (".", "Sólido e plano (1)"), ("a", "Arenoso (4)"),
                               ("r", "Rochoso (10)"), ("p", "Pântano (20)")):
            tk.Label(legenda, bg=CORES[simbolo], width=1, relief="solid", bd=1).pack(side="left")
            tk.Label(legenda, text=texto).pack(side="left", padx=(2, 6))

        tk.Label(esquerda, text="Carinha = agente   $ = recompensa   Estrela = saída",
                 fg=CINZA).pack(anchor="w", pady=(4, 0))

    def montar_direita(self):
        direita = tk.Frame(self.raiz)
        direita.grid(row=0, column=1, sticky="ns", padx=(15, 8), pady=(9, 0))

        caixa = ttk.LabelFrame(direita, text="Algoritmo", padding=(10, 8, 10, 6))
        caixa.pack(fill="x")
        self.algoritmo = tk.StringVar(value="4")
        for chave, nome in OPCOES:
            ttk.Radiobutton(caixa, text=nome, value=chave, variable=self.algoritmo).pack(anchor="w", pady=(0, 1))
        ttk.Button(caixa, text="Executar", command=self.executar).pack(fill="x", pady=(9, 4))

        outras = ttk.LabelFrame(direita, text="Outras opções", padding=(10, 8, 10, 6))
        outras.pack(fill="x", pady=(10, 0))
        for texto, comando in (("Comparar algoritmos", self.comparar),
                               ("Testar sala sem entrada", self.testar_sala),
                               ("Limpar", self.limpar)):
            ttk.Button(outras, text=texto, command=comando).pack(fill="x", pady=3)

        self.rotulo_destino = tk.Label(direita, text="")
        self.rotulo_destino.pack(anchor="w", pady=(10, 0))
        tk.Label(direita, text="Resultado:").pack(anchor="w", pady=(8, 0))
        self.resultado = tk.Text(direita, width=46, height=16, font=("Consolas", 9),
                                 relief="sunken", bd=1, wrap="none", state="disabled")
        self.resultado.pack(fill="both", expand=True)

    # ---------- desenho ----------

    def casa(self, pos, folga=0):
        # retângulo da casa na tela (x0, y0, x1, y1), com uma folga pra dentro
        x, y = pos
        return (x * self.tam + folga, y * self.tam + folga,
                (x + 1) * self.tam - folga, (y + 1) * self.tam - folga)

    def desenhar_mapa(self):
        self.tela.delete("all")
        for y, linha in enumerate(self.mapa.grade):
            for x, simbolo in enumerate(linha):
                self.tela.create_rectangle(*self.casa((x, y)), fill=CORES[simbolo], outline="#8c8c8c")
        self.moedas = {pos: self.desenhar_moeda(pos) for pos in self.mapa.recompensas}
        self.desenhar_estrela(self.mapa.premio)
        if self.destino != self.mapa.premio:
            self.tela.create_rectangle(*self.casa(self.destino, 2), outline="#d00000", width=2)
        self.desenhar_carinha(self.mapa.inicio)

    def desenhar_moeda(self, pos):
        etiqueta = f"moeda_{pos[0]}_{pos[1]}"
        x0, y0, x1, y1 = self.casa(pos, round(self.tam / 8))
        self.tela.create_oval(x0, y0, x1, y1, fill="#ffd500", outline="#ddb32a", tags=etiqueta)
        self.tela.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="$", font=("Arial", -round(self.tam * 13 / 24), "bold"),
                              tags=etiqueta)
        return etiqueta

    def desenhar_estrela(self, pos):
        x0, y0, x1, y1 = self.casa(pos)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        pontos = []
        for i in range(10):  # 5 pontas: alterna raio grande e raio pequeno
            raio = self.tam * 0.44 if i % 2 == 0 else self.tam * 0.18
            angulo = math.radians(-90 + 36 * i)
            pontos += [cx + raio * math.cos(angulo), cy + raio * math.sin(angulo)]
        self.tela.create_polygon(pontos, fill="#f00000", outline="#8b0000")

    def desenhar_carinha(self, pos):
        x0, y0, x1, y1 = self.casa(pos, round(self.tam / 8))
        cx, cy, t = (x0 + x1) / 2, (y0 + y1) / 2, self.tam
        self.tela.create_oval(x0, y0, x1, y1, fill="#ffff33", outline="black", width=2, tags="agente")
        for lado in (-1, 1):  # olhos
            ox, oy = cx + lado * t * 0.15, cy - t * 0.12
            self.tela.create_oval(ox - t * 0.07, oy - t * 0.07, ox + t * 0.07, oy + t * 0.07,
                                  fill="black", tags="agente")
        self.tela.create_arc(cx - t * 0.23, cy - t * 0.2, cx + t * 0.23, cy + t * 0.2,
                             start=200, extent=140, style="arc", width=2, tags="agente")

    # ---------- botões ----------

    def executar(self):
        self.parar_animacao()
        chave = self.algoritmo.get()
        nome = dict(OPCOES)[chave]
        funcao = ALGORITMOS[chave][1]
        recompensas = self.mapa.recompensas & self.chega  # recompensa presa em sala fechada fica de fora
        rota, expandidos, na_memoria, tempo_ms = rodar(funcao, self.mapa, self.mapa.inicio, self.destino, recompensas)

        self.desenhar_mapa()

        linhas = [nome, ""]
        if rota is None:
            linhas.append("Não existe caminho até o destino.")
        else:
            custo, coletadas, custo_liquido = percorrer(self.mapa, rota)
            linhas += [f"Custo do caminho: {custo}", f"Passos: {len(rota) - 1}",
                       f"Recompensas pegas: {len(coletadas)}", f"Custo líquido: {custo_liquido}"]
        linhas += [f"Nós expandidos: {len(expandidos)}", f"Nós na memória: {na_memoria}",
                   f"Tempo: {tempo_ms:.2f} ms"]
        if chave in ("1", "2"):
            vistas = len(set(expandidos) & self.mapa.recompensas)
            linhas.append(f"Recompensas vistas na busca: {vistas}")
        texto = "\n".join(linhas)

        if rota is None:
            self.escrever_resultado(texto)
            self.mostrar_status("Não existe caminho: a busca esvaziou a fronteira sem chegar no destino.")
            self.avisar_sem_caminho()
        else:
            self.escrever_resultado(f"{nome}\n\nExecutando...")
            atraso = int(min(120, 8000 / len(rota)))  # rota comprida anda mais rápido (no máximo uns 8 s)
            self.andar(nome, rota, 0, atraso, 0, 0, texto)

    def andar(self, nome, rota, i, atraso, custo, pegas, texto):
        pos = rota[i]
        if i > 0:
            anterior = rota[i - 1]
            custo += self.mapa.custo(pos)
            self.tela.create_oval(*self.casa(anterior, self.tam * 2 // 5), fill=COR_ROTA, outline="")
            self.tela.move("agente", (pos[0] - anterior[0]) * self.tam, (pos[1] - anterior[1]) * self.tam)
        if pos in self.moedas:
            self.tela.delete(self.moedas.pop(pos))
            pegas += 1
        self.tela.tag_raise("agente")
        self.mostrar_status(f"{nome}: passo {i} de {len(rota) - 1} | custo até aqui: {custo} | recompensas: {pegas}")

        if i + 1 < len(rota):
            self.animacao = self.raiz.after(atraso, self.andar, nome, rota, i + 1, atraso, custo, pegas, texto)
        else:
            self.animacao = None
            self.escrever_resultado(texto)
            self.mostrar_status(f"{nome}: o agente chegou no destino.")

    def comparar(self):
        self.parar_animacao()
        self.desenhar_mapa()
        recompensas = self.mapa.recompensas & self.chega
        linhas, vistas = calcular(self.mapa, self.mapa.inicio, self.destino, recompensas)

        texto = ["Comparação dos algoritmos",
                 f"Grafo: {self.mapa.num_vertices()} vértices e {self.mapa.num_arestas()} arestas", "",
                 f"{'Algoritmo':<14}{'Custo':>6}{'$':>3}{'Líq.':>6}{'Nós':>6}{'ms':>7}"]
        for nome, _, custo, _, pegas, liquido, expandidos, _, tempo in linhas:
            texto.append(f"{nome:<14}{custo:>6}{pegas:>3}{liquido:>6}{expandidos:>6}{tempo:>7}")
        texto += ["", "Custo líquido = custo - 10 por recompensa.",
                  "Recompensas vistas pela busca cega:",
                  f"Largura {vistas['Largura']}, Profundidade {vistas['Profundidade']}"]
        self.escrever_resultado("\n".join(texto))

        arquivo = grafico(linhas)
        self.mostrar_status("Comparação pronta." + (" Gráfico salvo em comparativo.png." if arquivo else ""))
        if all(linha[1] == "não" for linha in linhas):
            self.avisar_sem_caminho()

    def testar_sala(self):
        if not self.salas:
            self.mostrar_status("Esse mapa não tem sala sem entrada.")
            return
        sala = sorted(self.salas[0])
        self.destino = sala[len(sala) // 2]  # uma casa do meio da sala fechada
        self.atualizar_destino()
        self.executar()

    def limpar(self):
        self.parar_animacao()
        self.destino = self.mapa.premio
        self.atualizar_destino()
        self.desenhar_mapa()
        self.escrever_resultado("")
        self.mostrar_status(MENSAGEM_INICIAL)

    # ---------- mouse ----------

    def mouse_em_cima(self, evento):
        pos = (evento.x // self.tam, evento.y // self.tam)
        if not self.mapa.dentro(pos):
            return
        x, y = pos
        if pos == self.mapa.premio:
            nome = "saída"
        elif pos in self.moedas:
            nome = "recompensa"
        else:
            nome = NOME_TERRENO.get(self.mapa.grade[y][x], "sólido e plano")
        if pos in self.becos:
            nome += " (beco sem saída)"
        elif not self.mapa.eh_parede(pos) and pos not in self.chega:
            nome += " (sala sem entrada)"
        self.info.config(text=f"x={x}, y={y}  {nome}")

    def clicou_no_mapa(self, evento):
        pos = (evento.x // self.tam, evento.y // self.tam)
        if not self.mapa.dentro(pos):
            return
        if self.mapa.eh_parede(pos):
            self.mostrar_status("Esse ponto é uma parede, escolha outro destino.")
        elif pos == self.mapa.inicio:
            self.mostrar_status("O agente já está nesse ponto, escolha outro destino.")
        else:
            self.parar_animacao()
            self.destino = pos
            self.atualizar_destino()
            self.desenhar_mapa()
            self.mostrar_status("Destino escolhido. Clique em Executar.")

    # ---------- auxiliares ----------

    def atualizar_destino(self):
        x, y = self.destino
        if self.destino == self.mapa.premio:
            texto = f"Destino: saída ({x}, {y})"
        elif self.destino not in self.chega:
            texto = f"Destino: sala sem entrada ({x}, {y})"
        else:
            texto = f"Destino: ({x}, {y})"
        self.rotulo_destino.config(text=texto)

    def avisar_sem_caminho(self):
        # janelinha de aviso por cima da tela; o mapa e o resultado aparecem antes dela
        self.raiz.update_idletasks()
        x, y = self.destino
        messagebox.showwarning("Sem caminho",
                               f"Não existe caminho para chegar no destino ({x}, {y}).\n"
                               "Ele fica numa sala sem entrada, cercada por paredes.",
                               parent=self.raiz)

    def escrever_resultado(self, texto):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", "end")
        self.resultado.insert("1.0", texto)
        self.resultado.config(state="disabled")

    def parar_animacao(self):
        if self.animacao is not None:
            self.raiz.after_cancel(self.animacao)
            self.animacao = None

    def mostrar_status(self, texto):
        self.status.config(text=texto)


if __name__ == "__main__":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # deixa a janela nítida quando o Windows usa zoom
    except Exception:
        pass
    raiz = tk.Tk()
    Janela(raiz)
    raiz.mainloop()
