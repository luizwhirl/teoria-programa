import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import sys

class AutomatoTravessia:
    """
    Modela o problema da Travessia (Lobo, Cabra, Repolho) como um Autômato Finito.
    """

    def __init__(self, estado_inicial=('E', 'E', 'E', 'E')):
        """
        Define os componentes do autômato finito.
        
        Args:
            estado_inicial (tuple): A configuração inicial de onde começar a resolução.
        """
        if not self.is_valid_state(estado_inicial):
            raise ValueError(f"O estado inicial fornecido {estado_inicial} é inválido e viola as regras.")
            
        self.estado_inicial = estado_inicial
        self.estado_final = ('D', 'D', 'D', 'D')
        self.alfabeto = ["lobo", "cabra", "repolho", "sozinho"]
        self.item_map = {"lobo": 1, "cabra": 2, "repolho": 3}

    def is_valid_state(self, estado):
        _fazendeiro, lobo, cabra, repolho = estado
        if lobo == cabra and _fazendeiro != lobo: return False
        if cabra == repolho and _fazendeiro != cabra: return False
        return True

    def transition(self, estado_atual, acao):
        fazendeiro_pos = estado_atual[0]
        if acao != "sozinho":
            item_index = self.item_map[acao]
            if estado_atual[item_index] != fazendeiro_pos: return None
        proxima_pos_fazendeiro = 'D' if fazendeiro_pos == 'E' else 'E'
        proximo_estado = list(estado_atual)
        proximo_estado[0] = proxima_pos_fazendeiro
        if acao != "sozinho":
            proximo_estado[self.item_map[acao]] = proxima_pos_fazendeiro
        proximo_estado_tupla = tuple(proximo_estado)
        return proximo_estado_tupla if self.is_valid_state(proximo_estado_tupla) else None

    def resolver_bfs(self):
        if self.estado_inicial == self.estado_final: return [[self.estado_inicial]]
        fila = deque([[self.estado_inicial]])
        visitados = {self.estado_inicial}
        while fila:
            caminho_atual = fila.popleft()
            ultimo_estado = caminho_atual[-1]
            if ultimo_estado == self.estado_final: return caminho_atual
            for acao in self.alfabeto:
                novo_estado = self.transition(ultimo_estado, acao)
                if novo_estado and novo_estado not in visitados:
                    visitados.add(novo_estado)
                    novo_caminho = list(caminho_atual)
                    novo_caminho.append(novo_estado)
                    fila.append(novo_caminho)
        return None

# classe da interface gráfica nesse diabo
    class TravessiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solucionador do Problema da Travessia")
        self.geometry("950x700") # Janela um pouco maior para acomodar o desenho

        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Estado Inicial (F L C R):").pack(side=tk.LEFT, padx=(0, 5))
        
        self.estado_entry = ttk.Entry(control_frame, width=20)
        self.estado_entry.insert(0, "E E E E")
        self.estado_entry.pack(side=tk.LEFT, padx=5)

        self.solve_button = ttk.Button(control_frame, text="Resolver e Desenhar", command=self.resolver_e_desenhar)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _get_movimento_label(self, estado_anterior, estado_atual, item_map):
        origem = "Esquerda" if estado_anterior[0] == 'E' else "Direita"
        destino = "Direita" if estado_atual[0] == 'D' else "Esquerda"
        
        item_movido = "sozinho"
        for item, index in item_map.items():
            if estado_anterior[index] != estado_atual[index]:
                item_movido = item
                break
        
        if item_movido == "sozinho":
             return f"Volta sozinho"
        else:
             return f"Leva o/a {item_movido}"

    def resolver_e_desenhar(self):
        self.canvas.delete("all")
        entrada_usuario = self.estado_entry.get().strip().upper()
        partes = entrada_usuario.split()

        if len(partes) != 4 or not all(p in ['E', 'D'] for p in partes):
            messagebox.showerror("Erro de Formato", "Formato inválido. Insira 4 valores ('E' ou 'D') separados por espaço.\nExemplo: E E E E")
            return
            
        estado_inicial_usuario = tuple(partes)

        automato_temp = AutomatoTravessia()
        if not automato_temp.is_valid_state(estado_inicial_usuario):
            messagebox.showerror("Estado Inválido", "O estado inicial viola as regras do problema.\n(Lobo/Cabra ou Cabra/Repolho não podem ficar sozinhos).")
            return

        automato = AutomatoTravessia(estado_inicial=estado_inicial_usuario)
        caminho_solucao = automato.resolver_bfs()

        if not caminho_solucao:
            messagebox.showinfo("Sem Solução", "Não foi encontrada uma solução a partir do estado fornecido.")
            return
        
        self.desenhar_solucao(caminho_solucao, automato.item_map)

    def desenhar_solucao(self, caminho, item_map):
        """
        NOVO MÉTODO DE DESENHO:
        - O texto fica fora dos nós.
        - O layout é em "serpente" para caber na tela.
        """
        # Parâmetros de layout
        nodes_per_row = 4
        start_x, start_y = 120, 80
        x_step, y_step = 220, 160 # Aumenta o espaçamento para o texto
        node_radius = 30
        
        posicoes_nos = {} 

        for i, estado in enumerate(caminho):
            # Lógica para layout em serpente
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            if row % 2 == 0:  # Linhas pares: da esquerda para a direita
                x = start_x + col * x_step
            else:  # Linhas ímpares: da direita para a esquerda
                x = start_x + (nodes_per_row - 1 - col) * x_step
            
            y = start_y + row * y_step
            
            posicoes_nos[i] = (x, y)

            # Desenha a seta e o rótulo da transição (a partir do segundo nó)
            if i > 0:
                px, py = posicoes_nos[i-1] # Posição do nó anterior
                
                # Desenha a linha da seta conectando o centro dos nós
                self.canvas.create_line(px, py, x, y, arrow=tk.LAST, fill="darkgreen", width=1.5)

                # Calcula a posição do rótulo da seta (no meio do caminho)
                label_x = (px + x) / 2
                label_y = (py + y) / 2 - 15 # Desloca um pouco para cima da linha
                
                label_text = self._get_movimento_label(caminho[i-1], estado, item_map)
                # Adiciona um fundo branco ao texto para não colidir com a seta
                bbox = self.canvas.create_text(label_x, label_y, text=label_text, font=("Arial", 10, "italic"), fill="darkgreen")
                coords = self.canvas.bbox(bbox)
                self.canvas.create_rectangle(coords, fill="white", outline="white")
                self.canvas.lift(bbox) # Traz o texto para a frente

            # Desenha o nó (círculo)
            self.canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill="lightblue", outline="black", width=2)
            
            # Escreve o nome do estado (q_i) ACIMA do círculo
            self.canvas.create_text(x, y - node_radius - 15, text=f"q{i}", font=("Arial", 14, "bold"))
            
            # Escreve a configuração ABAIXO do círculo
            self.canvas.create_text(x, y + node_radius + 15, text=str(estado), font=("Arial", 10), fill="black")

if __name__ == "__main__":
    app = TravessiaApp()
    app.mainloop()
