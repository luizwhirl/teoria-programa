import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import sys
import math

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "A biblioteca Pillow é necessária. Por favor, instale-a com 'pip install Pillow'")
    sys.exit()

class AutomatoTravessia:
    def __init__(self, estado_inicial=('E', 'E', 'E', 'E')):
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

class TravessiaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Solucionador do Problema da Travessia")
        self.geometry("1000x750")

        self.caminho_solucao = None
        self.passo_atual_animacao = 0
        self.animacao_em_curso = False

        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Estado Inicial (F L C R):").pack(side=tk.LEFT, padx=(0, 5))
        
        self.estado_entry = ttk.Entry(control_frame, width=20)
        self.estado_entry.insert(0, "E E E E")
        self.estado_entry.pack(side=tk.LEFT, padx=5)

        self.solve_button = ttk.Button(control_frame, text="Resolver e Preparar Visualizações", command=self.resolver_e_preparar)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        tab_grafo = ttk.Frame(self.notebook)
        self.notebook.add(tab_grafo, text="Grafo da Solução")
        self.canvas_grafo = tk.Canvas(tab_grafo, bg="white", highlightthickness=0)
        self.canvas_grafo.pack(fill=tk.BOTH, expand=True)

        self.tab_animacao = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_animacao, text="Animação da Travessia", state="disabled")
        
        anim_control_frame = ttk.Frame(self.tab_animacao, padding=(0, 10))
        anim_control_frame.pack(fill=tk.X)
        self.start_anim_button = ttk.Button(anim_control_frame, text="Iniciar Animação", command=self.iniciar_animacao, state="disabled")
        self.start_anim_button.pack(side=tk.LEFT, padx=5)
        self.reset_anim_button = ttk.Button(anim_control_frame, text="Resetar", command=self.preparar_animacao, state="disabled")
        self.reset_anim_button.pack(side=tk.LEFT, padx=5)

        self.canvas_animacao = tk.Canvas(self.tab_animacao, highlightthickness=0)
        self.canvas_animacao.pack(fill=tk.BOTH, expand=True)

        self.item_visuals = {
            "fazendeiro": {"arquivo": "fazendeiro.png", "id": None, "size": (60, 60)},
            "lobo":       {"arquivo": "lobo.png",       "id": None, "size": (55, 55)},
            "cabra":      {"arquivo": "cabra.png",      "id": None, "size": (55, 55)},
            "repolho":    {"arquivo": "repolho.png",    "id": None, "size": (50, 50)}
        }
        self.loaded_images = {}
        self._load_images()

        self.id_barco = None
        self.id_texto_acao = None

    def _load_images(self):
        try:
            for key, visual in self.item_visuals.items():
                img = Image.open(visual["arquivo"])
                img = img.resize(visual["size"], Image.Resampling.LANCZOS)
                self.loaded_images[key] = ImageTk.PhotoImage(img)
            
            barco_img = Image.open("barco.png")
            barco_img = barco_img.resize((150, 100), Image.Resampling.LANCZOS)
            self.loaded_images["barco"] = ImageTk.PhotoImage(barco_img)

        except FileNotFoundError as e:
            messagebox.showerror("Arquivo não encontrado", f"Não foi possível encontrar: {e.filename}\nCertifique-se que as imagens (.png) estão na mesma pasta.")
            self.destroy()

    def _get_movimento_label(self, estado_anterior, estado_atual, item_map):
        destino_char = estado_atual[0]
        destino = "Direita" if destino_char == 'D' else "Esquerda"
        item_movido = "sozinho"
        for item, index in item_map.items():
            if estado_anterior[index] != estado_atual[index]:
                item_movido = item
                break
        
        if item_movido == "sozinho":
            return f"Fazendeiro volta sozinho para a margem {destino}"
        else:
            return f"Leva o(a) {item_movido} para a margem {destino}"

    def resolver_e_preparar(self):
        self.canvas_grafo.delete("all")
        self.notebook.tab(1, state="disabled")
        self.start_anim_button.config(state="disabled")
        self.reset_anim_button.config(state="disabled")

        entrada = self.estado_entry.get().strip().upper()
        partes = entrada.split()

        if len(partes) != 4 or not all(p in ['E', 'D'] for p in partes):
            messagebox.showerror("Erro de Formato", "Formato inválido. Insira 4 valores ('E' ou 'D') separados por espaço.\nExemplo: E E E E")
            return
            
        estado_inicial_usuario = tuple(partes)

        automato_temp = AutomatoTravessia()
        if not automato_temp.is_valid_state(estado_inicial_usuario):
            messagebox.showerror("Estado Inválido", "O estado inicial viola as regras do problema.\n(Lobo/Cabra ou Cabra/Repolho não podem ficar sozinhos).")
            return

        automato = AutomatoTravessia(estado_inicial=estado_inicial_usuario)
        self.caminho_solucao = automato.resolver_bfs()

        if not self.caminho_solucao:
            messagebox.showinfo("Sem Solução", "Não foi encontrada uma solução a partir do estado fornecido.")
            return
        
        self.desenhar_solucao_grafo(self.caminho_solucao, automato.item_map)
        self.preparar_animacao()
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)
        self.start_anim_button.config(state="normal")
        self.reset_anim_button.config(state="normal")

    def desenhar_solucao_grafo(self, caminho, item_map):
        self.canvas_grafo.delete("all")
        nodes_per_row = 4
        start_x, start_y = 120, 80
        x_step, y_step = 220, 160
        node_radius = 30
        
        posicoes_nos = {} 

        for i, estado in enumerate(caminho):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            if row % 2 == 0:
                x = start_x + col * x_step
            else:
                x = start_x + (nodes_per_row - 1 - col) * x_step
            y = start_y + row * y_step
            posicoes_nos[i] = (x, y)

            if i > 0:
                px, py = posicoes_nos[i-1]
                self.canvas_grafo.create_line(px, py, x, y, arrow=tk.LAST, fill="darkgreen", width=1.5)
                
                label_x = (px + x) / 2
                label_y = (py + y) / 2 - 15
                
                movimento = self._get_movimento_label(caminho[i-1], estado, item_map).split(" para")[0]
                bbox_item = self.canvas_grafo.create_text(label_x, label_y, text=movimento, font=("Arial", 10, "italic"), fill="darkgreen")
                coords = self.canvas_grafo.bbox(bbox_item)
                self.canvas_grafo.create_rectangle(coords, fill="white", outline="white")
                self.canvas_grafo.lift(bbox_item)

            self.canvas_grafo.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill="lightblue", outline="black", width=2)
            self.canvas_grafo.create_text(x, y - node_radius - 15, text=f"q{i}", font=("Arial", 14, "bold"))
            self.canvas_grafo.create_text(x, y + node_radius + 20, text=str(estado), font=("Arial", 10), fill="black")

    # metodos de animação
    def preparar_animacao(self):
        if self.animacao_em_curso: return

        self.passo_atual_animacao = 0
        self.canvas_animacao.delete("all")

        self.update_idletasks() 
        w, h = self.canvas_animacao.winfo_width(), self.canvas_animacao.winfo_height()
        if w < 2: w, h = 950, 600
        
        # margens
        self.margem_esq_x_fim = w * 0.25
        self.margem_dir_x_inicio = w * 0.75
        self.nivel_grama = h - 120
        
        # cenário (nesse caso daqui é o gradiente)
        for i in range(int(h * 0.7)):
            r = 135 + int((90 * i) / (h * 0.7))
            g = 206 + int((40 * i) / (h * 0.7))
            b = 250
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas_animacao.create_line(0, i, w, i, fill=color)
        
        # nuvens e sol
        self.canvas_animacao.create_oval(w * 0.8, h * 0.1, w * 0.9, h * 0.25, fill="#FFD700", outline="#FFA500")
        self.canvas_animacao.create_oval(w * 0.1, h * 0.15, w * 0.25, h * 0.3, fill="white", outline="")
        self.canvas_animacao.create_oval(w * 0.18, h * 0.1, w * 0.3, h * 0.25, fill="white", outline="")

        # rio e grandiente do... rio porra
        for i in range(int(h * 0.7), h):
            b = 180 - int((90 * (i - h * 0.7)) / (h * 0.3))
            color = f'#4682{b:02x}'
            self.canvas_animacao.create_line(0, i, w, i, fill=color)

        # margens - terra e grama
        self.canvas_animacao.create_rectangle(0, self.nivel_grama, self.margem_esq_x_fim, h, fill="#A0522D", outline="#6B4226", width=2)
        self.canvas_animacao.create_rectangle(self.margem_dir_x_inicio, self.nivel_grama, w, h, fill="#A0522D", outline="#6B4226", width=2)
        self.canvas_animacao.create_rectangle(0, self.nivel_grama, self.margem_esq_x_fim, self.nivel_grama + 10, fill="#228B22", outline="")
        self.canvas_animacao.create_rectangle(self.margem_dir_x_inicio, self.nivel_grama, w, self.nivel_grama + 10, fill="#228B22", outline="")

        self.canvas_animacao.create_text(self.margem_esq_x_fim / 2, self.nivel_grama + 40, text="MARGEM ESQUERDA", font=("Arial", 12, "bold"), fill="white")
        self.canvas_animacao.create_text(self.margem_dir_x_inicio + (w-self.margem_dir_x_inicio)/2, self.nivel_grama + 40, text="MARGEM DIREITA", font=("Arial", 12, "bold"), fill="white")

        self.desenhar_estado_animacao(self.caminho_solucao[0])
        self.start_anim_button.config(state="normal")

    def desenhar_estado_animacao(self, estado):
        self.canvas_animacao.delete("personagem")
        
        fazendeiro_pos, lobo_pos, cabra_pos, repolho_pos = estado
        mapa_estado = {"fazendeiro": fazendeiro_pos, "lobo": lobo_pos, "cabra": cabra_pos, "repolho": repolho_pos}
        
        itens_esquerda = [item for item, pos in mapa_estado.items() if pos == 'E']
        itens_direita = [item for item, pos in mapa_estado.items() if pos == 'D']

        # y - personagens
        y_pos = self.nivel_grama - 25 
        x_spacing = 65

        # esq
        start_x_esq = (self.margem_esq_x_fim / 2) - (len(itens_esquerda) - 1) * x_spacing / 2
        for i, item_key in enumerate(itens_esquerda):
            x = start_x_esq + i * x_spacing
            visual = self.item_visuals[item_key]
            visual["id"] = self.canvas_animacao.create_image(x, y_pos, image=self.loaded_images[item_key], tags="personagem")

        # dir
        meio_margem_dir = self.margem_dir_x_inicio + (self.canvas_animacao.winfo_width() - self.margem_dir_x_inicio) / 2
        start_x_dir = meio_margem_dir - (len(itens_direita) - 1) * x_spacing / 2
        for i, item_key in enumerate(itens_direita):
            x = start_x_dir + i * x_spacing
            visual = self.item_visuals[item_key]
            visual["id"] = self.canvas_animacao.create_image(x, y_pos, image=self.loaded_images[item_key], tags="personagem")


    def iniciar_animacao(self):
        if self.animacao_em_curso: return
        
        self.animacao_em_curso = True
        self.solve_button.config(state="disabled")
        self.start_anim_button.config(state="disabled")
        self.reset_anim_button.config(state="disabled")
        
        self.animar_passo()

    def animar_passo(self):
        if self.passo_atual_animacao >= len(self.caminho_solucao) - 1:
            self.canvas_animacao.delete(self.id_texto_acao)
            self.id_texto_acao = self.canvas_animacao.create_text(self.winfo_width()/2, 50, text="Travessia Concluída! Parabéns!", font=("Arial", 22, "bold"), fill="#32CD32")
            self.animacao_em_curso = False
            self.solve_button.config(state="normal")
            self.reset_anim_button.config(state="normal")
            return

        estado_anterior = self.caminho_solucao[self.passo_atual_animacao]
        estado_seguinte = self.caminho_solucao[self.passo_atual_animacao + 1]

        passageiro_key = None
        for item, index in AutomatoTravessia().item_map.items():
            if estado_anterior[index] != estado_seguinte[index]:
                passageiro_key = item
                break
        
        direcao_de = estado_anterior[0]
        
        y_barco = self.nivel_grama - 40
        x_partida = self.margem_esq_x_fim + 75 if direcao_de == 'E' else self.margem_dir_x_inicio - 75
        x_chegada = self.margem_dir_x_inicio - 75 if direcao_de == 'E' else self.margem_esq_x_fim + 75
        
        label_movimento = self._get_movimento_label(estado_anterior, estado_seguinte, AutomatoTravessia().item_map)
        self.canvas_animacao.delete(self.id_texto_acao)
        self.id_texto_acao = self.canvas_animacao.create_text(self.winfo_width()/2, 50, text=label_movimento, font=("Arial", 16, "italic"), fill="black")

        self.id_barco = self.canvas_animacao.create_image(x_partida, y_barco, image=self.loaded_images["barco"], tags="barco")
        
        fazendeiro_id = self.item_visuals["fazendeiro"]["id"]
        fx, fy = self.canvas_animacao.coords(fazendeiro_id)
        # ajustar posição do fazendeiro no baroco
        self.canvas_animacao.move(fazendeiro_id, x_partida - fx - 15, y_barco - fy + 10)
        self.canvas_animacao.tag_raise(fazendeiro_id) 
        
        if passageiro_key:
            passageiro_id = self.item_visuals[passageiro_key]["id"]
            px, py = self.canvas_animacao.coords(passageiro_id)
            # ajusta passagero
            self.canvas_animacao.move(passageiro_id, x_partida - px + 25, y_barco - py + 15) 
            self.canvas_animacao.tag_raise(passageiro_id)

        self.movimento_suave(x_chegada - x_partida, 0, passageiro_key)

    def movimento_suave(self, dx, dy, passageiro_key, passos=120, passo_atual=0):
        if passo_atual < passos:
            movimento_x = dx / passos
            # movimentação vap vup tipo onda
            movimento_y = math.sin(passo_atual * math.pi / (passos / 4)) * 0.25 

            self.canvas_animacao.move(self.id_barco, movimento_x, movimento_y)
            self.canvas_animacao.move(self.item_visuals["fazendeiro"]["id"], movimento_x, movimento_y)
            if passageiro_key:
                self.canvas_animacao.move(self.item_visuals[passageiro_key]["id"], movimento_x, movimento_y)
            
            self.after(20, lambda: self.movimento_suave(dx, dy, passageiro_key, passos, passo_atual + 1))
        else:
            self.canvas_animacao.delete(self.id_barco)
            self.passo_atual_animacao += 1
            self.desenhar_estado_animacao(self.caminho_solucao[self.passo_atual_animacao])
            self.after(800, self.animar_passo)

if __name__ == "__main__":
    app = TravessiaApp()
    app.mainloop()