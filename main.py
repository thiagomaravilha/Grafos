# pip install Pillow

from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog
import heapq
import os

class Grafo:
    def __init__(self, imagens):
        self.grafo = {}
        self.largura, self.altura = imagens[0].size
        self.profundidade = len(imagens)

        for z in range(self.profundidade):
            for x in range(self.largura):
                for y in range(self.altura):
                    pixel = imagens[z].getpixel((x, y))
                    posicao = (x, y, z)

                    if pixel != (0, 0, 0):  # Se o pixel não for preto
                        vizinhos = self.obter_vizinhos(posicao)
                        self.grafo[posicao] = {vizinho: self.obter_peso(imagens[vizinho[2]].getpixel((vizinho[0], vizinho[1]))) for vizinho in vizinhos if imagens[vizinho[2]].getpixel((vizinho[0], vizinho[1])) != (0, 0, 0)}
                    else:  # Se o pixel for preto (adiciona o pixel ao grafo, mas sem vizinhos)
                        self.grafo[posicao] = {}

    def obter_vizinhos(self, posicao):
        x, y, z = posicao
        vizinhos = [(x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)]
        return [(nx, ny, nz) for nx, ny, nz in vizinhos if 0 <= nx < self.largura and 0 <= ny < self.altura and 0 <= nz < self.profundidade]

    def obter_peso(self, pixel):
        if pixel == (128, 128, 128):  # Cinza escuro
            return 2
        elif pixel == (196, 196, 196):  # Cinza claro
            return 1.5
        elif pixel == (255, 255, 255):  # Branco
            return 1
        else:  # Vermelho ou verde
            return 5

    def dijkstra(self, inicio, objetivos, tamanho_ponto_vermelho, imagens):
        fila_prioridade = [(0, inicio, [])]
        visitados = set()
        menor_caminho = None

        while fila_prioridade:
            custo, atual, caminho = heapq.heappop(fila_prioridade)

            if atual in objetivos:
                if menor_caminho is None or custo < menor_caminho[0]:
                    menor_caminho = (custo, caminho)

            if atual not in visitados:
                visitados.add(atual)
                for vizinho, peso in self.grafo[atual].items():
                    if self.verificar_movimento(atual, vizinho, tamanho_ponto_vermelho, imagens):
                        heapq.heappush(fila_prioridade, (custo + peso, vizinho, caminho + [self.obter_direcao(atual, vizinho)]))

        return menor_caminho[1] if menor_caminho else None

    @staticmethod
    def obter_direcao(atual, vizinho):
        dx, dy, dz = vizinho[0] - atual[0], vizinho[1] - atual[1], vizinho[2] - atual[2]

        if dx == 1:
            return "→"
        elif dx == -1:
            return "←"
        elif dy == -1:
            return "↑"
        elif dy == 1:
            return "↓"
        elif dz == -1:
            return "⇩"
        elif dz == 1:
            return "⇧"

    def verificar_movimento(self, atual, vizinho, tamanho_ponto_vermelho, imagens):
        x1, y1, z1 = atual
        x2, y2, z2 = vizinho
        for x in range(tamanho_ponto_vermelho[0]):
            for y in range(tamanho_ponto_vermelho[1]):
                if 0 <= x1 + x < self.largura and 0 <= y1 + y < self.altura:  # Verifica se a coordenada está dentro dos limites da imagem
                    pixel = imagens[z1].getpixel((x1 + x, y1 + y))
                    if pixel == (0, 0, 0):  # Se encontrar um ponto preto no caminho
                        return False
                else:
                    return False  # Coordenada fora dos limites da imagem
        return True

class Aplicacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Trabalho Prático - AEDS 3")

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

        self.titulo = tk.Label(root, text="Planejamento de Manutenção", font=("Arial", 16, "bold") )
        self.titulo.pack()

        self.botao_selecionar = tk.Button(root, text="Selecionar Pasta", command=self.selecionar_pasta)
        self.botao_selecionar.pack()

    def selecionar_pasta(self):
        caminho_pasta = filedialog.askdirectory()

        if caminho_pasta:
            arquivos_imagem = sorted([os.path.join(caminho_pasta, nome) for nome in os.listdir(caminho_pasta) if nome.endswith('.bmp') or nome.endswith('.png') or nome.endswith('.jpg') or nome.endswith('.jpeg')])
            imagens = [Image.open(arquivo) for arquivo in arquivos_imagem]
            grafo = Grafo(imagens)

            # Encontrar coordenadas do equipamento (ponto vermelho)
            inicio, tamanho_ponto_vermelho = self.encontrar_coordenadas(imagens, (255, 0, 0))

            # Encontrar coordenadas das áreas de manutenção (pontos verdes)
            objetivos = self.encontrar_todas_coordenadas(imagens, (0, 255, 0))

            for img_idx, img in enumerate(imagens):
                caminho = grafo.dijkstra(inicio, objetivos, tamanho_ponto_vermelho, imagens)
                if caminho:
                    print("É possível deslocar o equipamento na imagem {}:".format(img_idx + 1))
                    caminho_atual = []
                    img_copy = img.copy()
                    desenho = ImageDraw.Draw(img_copy)
                    x, y, z = inicio
                    for direcao in caminho:
                        if direcao == "→":
                            x += 1
                        elif direcao == "←":
                            x -= 1
                        elif direcao == "↑":
                            y -= 1
                        elif direcao == "↓":
                            y += 1
                        elif direcao == "⇩":
                            z -= 1
                        elif direcao == "⇧":
                            z += 1
                        caminho_atual.append(direcao)
                        desenho.rectangle([(x, y), (x + tamanho_ponto_vermelho[0], y + tamanho_ponto_vermelho[1])], outline=(255, 0, 0))  # Desenha retângulo vermelho
                        if z != inicio[2]:  # Troca de imagem
                            break
                    print(" ".join(caminho_atual))
                    img_copy.show()
                    inicio = (x, y, z)  # Atualiza a posição inicial para a próxima imagem
                else:
                    print("Não é possível deslocar o equipamento na imagem {}.".format(img_idx + 1))

    def encontrar_coordenadas(self, imagens, cor):
        tamanho_ponto_vermelho = (0, 0)  # Inicializa o tamanho do ponto vermelho como (0, 0)
        for z in range(len(imagens)):
            for x in range(imagens[z].width):
                for y in range(imagens[z].height):
                    if imagens[z].getpixel((x, y)) == cor:
                        tamanho_ponto_vermelho = self.obter_tamanho_ponto(imagens[z], cor, (x, y))
                        return (x, y, z), tamanho_ponto_vermelho
        return None, tamanho_ponto_vermelho

    def obter_tamanho_ponto(self, imagem, cor, ponto):
        largura, altura = imagem.size
        x, y = ponto
        tamanho_horizontal = 0
        tamanho_vertical = 0
        # Verifica o tamanho horizontal
        for i in range(x, largura):
            if imagem.getpixel((i, y)) == cor:
                tamanho_horizontal += 1
            else:
                break
        # Verifica o tamanho vertical
        for j in range(y, altura):
            if imagem.getpixel((x, j)) == cor:
                tamanho_vertical += 1
            else:
                break
        return tamanho_horizontal, tamanho_vertical

    def encontrar_todas_coordenadas(self, imagens, cor):
        coordenadas = []
        for z in range(len(imagens)):
            for x in range(imagens[z].width):
                for y in range(imagens[z].height):
                    if imagens[z].getpixel((x, y)) == cor:
                        coordenadas.append((x, y, z))
        return coordenadas

def main():
    root = tk.Tk()
    app = Aplicacao(root)
    root.mainloop()

if __name__ == "__main__":
    main()
