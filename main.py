import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import sys
import math

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Biblioteca Faltando", "A biblioteca Pillow (PIL) está faltando. Instale com: pip install pillow")
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
        self.title("Problema da Travessia e Simulação de Autômatos")
        self.geometry("1000x850")

        self.resizable(False, False)

        self.caminho_solucao = None
        self.passo_atual_animacao = 0
        self.animacao_em_curso = False
        
        self._job_id_grafo = None
        self._job_id_animacao = None
        self.grafo_caminho_data = None
        self.grafo_item_map_data = None

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        tab_resolucao = ttk.Frame(self.notebook)
        self.notebook.add(tab_resolucao, text="Solucionador do Problema")
        
        control_frame = ttk.Frame(tab_resolucao, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Estado Inicial (F L C R):").pack(side=tk.LEFT, padx=(0, 5))
        self.estado_entry = ttk.Entry(control_frame, width=20)
        self.estado_entry.insert(0, "E E E E")
        self.estado_entry.pack(side=tk.LEFT, padx=5)

        self.solve_button = ttk.Button(control_frame, text="Resolver e Preparar Visualizações", command=self.resolver_e_preparar)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.notebook_visualizacao = ttk.Notebook(tab_resolucao)
        self.notebook_visualizacao.pack(expand=True, fill="both", padx=10, pady=10)

        tab_grafo = ttk.Frame(self.notebook_visualizacao)
        self.notebook_visualizacao.add(tab_grafo, text="Grafo da Solução")
        self.canvas_grafo = tk.Canvas(tab_grafo, bg="white", highlightthickness=0)
        self.canvas_grafo.pack(fill=tk.BOTH, expand=True)
        self.canvas_grafo.bind("<Configure>", self._on_resize_grafo)

        self.tab_animacao = ttk.Frame(self.notebook_visualizacao)
        self.notebook_visualizacao.add(self.tab_animacao, text="Animação da Travessia", state="disabled")
        
        anim_control_frame = ttk.Frame(self.tab_animacao, padding=(0, 10))
        anim_control_frame.pack(fill=tk.X)
        self.start_anim_button = ttk.Button(anim_control_frame, text="Iniciar Animação", command=self.iniciar_animacao, state="disabled")
        self.start_anim_button.pack(side=tk.LEFT, padx=5)
        self.reset_anim_button = ttk.Button(anim_control_frame, text="Resetar", command=self.preparar_animacao, state="disabled")
        self.reset_anim_button.pack(side=tk.LEFT, padx=5)

        self.canvas_animacao = tk.Canvas(self.tab_animacao, highlightthickness=0)
        self.canvas_animacao.pack(fill=tk.BOTH, expand=True)
        self.canvas_animacao.bind("<Configure>", self._on_resize_animacao)
        
        self.setup_automato_fixo_tab()

        self.item_visuals = {
            "fazendeiro": {"arquivo": "assets/fazendeiro.png", "id": None, "size": (60, 60)},
            "lobo":       {"arquivo": "assets/lobo.png",       "id": None, "size": (55, 55)},
            "cabra":      {"arquivo": "assets/cabra.png",      "id": None, "size": (55, 55)},
            "repolho":    {"arquivo": "assets/repolho.png",    "id": None, "size": (50, 50)}
        }
        self.loaded_images = {}
        self._load_images()

        self.id_barco = None
        self.id_texto_acao = None

    def setup_automato_fixo_tab(self):
        self.tab_automato_fixo = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_automato_fixo, text="Simulação de Autômato (Fixo)")

        self.automato_fita = ['a', 'b', 'c', 'a', 'd', 'b', 'a']
        self.automato_estados = [f'q{i}' for i in range(8)]
        self.automato_caminho_puzzle = [
            ('E', 'E', 'E', 'E'), ('D', 'E', 'D', 'E'), ('E', 'E', 'D', 'E'), 
            ('D', 'D', 'D', 'E'), ('E', 'D', 'E', 'E'), ('D', 'D', 'E', 'D'),
            ('E', 'D', 'E', 'D'), ('D', 'D', 'D', 'D')
        ]
        self.automato_passo_atual = 0
        self.automato_animacao_em_curso = False

        control_frame = ttk.Frame(self.tab_automato_fixo)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        self.automato_start_button = ttk.Button(control_frame, text="Iniciar Simulação", command=self.iniciar_simulacao_fixa)
        self.automato_start_button.pack(side=tk.LEFT, padx=5)
        self.automato_reset_button = ttk.Button(control_frame, text="Resetar", command=self.resetar_simulacao_fixa, state="disabled")
        self.automato_reset_button.pack(side=tk.LEFT, padx=5)

        info_frame = ttk.Frame(self.tab_automato_fixo, borderwidth=2, relief="groove")
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.label_fita = ttk.Label(info_frame, text="Fita:", font=("Consolas", 12, "bold"))
        self.label_fita.pack(pady=2, padx=10, anchor="w")
        self.label_cabecote = ttk.Label(info_frame, text="Cabeçote:", font=("Consolas", 12))
        self.label_cabecote.pack(pady=2, padx=10, anchor="w")
        self.label_controle = ttk.Label(info_frame, text="Controle:", font=("Consolas", 14, "bold"))
        self.label_controle.pack(pady=5, padx=10, anchor="w")
        
        self.label_transicao = ttk.Label(info_frame, text="Transição:", font=("Consolas", 14, "bold"), foreground="blue")
        self.label_transicao.pack(pady=5, padx=10, anchor="w")

        paned_window = ttk.PanedWindow(self.tab_automato_fixo, orient=tk.VERTICAL)
        paned_window.pack(expand=True, fill=tk.BOTH)

        self.canvas_diagrama_automato = tk.Canvas(paned_window, bg="ivory", highlightthickness=0, height=250)
        paned_window.add(self.canvas_diagrama_automato, weight=2)
        
        self.canvas_animacao_automato = tk.Canvas(paned_window, highlightthickness=0)
        paned_window.add(self.canvas_animacao_automato, weight=3)
        
        self.canvas_diagrama_automato.bind("<Configure>", lambda e: self.desenhar_diagrama_automato_fixo())
        self.canvas_animacao_automato.bind("<Configure>", lambda e: self.resetar_simulacao_fixa() if not self.automato_animacao_em_curso else None)
        
        self.after(50, self.resetar_simulacao_fixa)
    
    def iniciar_simulacao_fixa(self):
        if self.automato_animacao_em_curso: return
        self.resetar_simulacao_fixa()
        self.automato_animacao_em_curso = True
        self.automato_start_button.config(state="disabled")
        self.automato_reset_button.config(state="disabled")
        self.notebook.tab(0, state="disabled")
        self.executar_passo_automato_fixo()

    def resetar_simulacao_fixa(self):
        self.automato_animacao_em_curso = False
        self.automato_passo_atual = 0
        self.automato_start_button.config(state="normal")
        self.automato_reset_button.config(state="disabled")
        self.notebook.tab(0, state="normal")
        self.canvas_animacao_automato.delete("all")
        self._desenhar_cenario_animacao(self.canvas_animacao_automato)
        self.desenhar_estado_animacao(self.automato_caminho_puzzle[0], self.canvas_animacao_automato)
        self.atualizar_info_automato_fixo()
        self.desenhar_diagrama_automato_fixo()

    def executar_passo_automato_fixo(self):
        if self.automato_passo_atual >= len(self.automato_fita):
            self.atualizar_info_automato_fixo()
            self.desenhar_diagrama_automato_fixo()

            self.canvas_animacao_automato.create_text(
                self.canvas_animacao_automato.winfo_width() / 2, 50,
                text="Fita processada. Simulação Concluída!", font=("Arial", 22, "bold"), fill="#32CD32", tags="fim_msg"
            )
            self.automato_animacao_em_curso = False
            self.automato_reset_button.config(state="normal")
            self.notebook.tab(0, state="normal")
            return

        self.atualizar_info_automato_fixo()
        self.desenhar_diagrama_automato_fixo()
        
        estado_anterior = self.automato_caminho_puzzle[self.automato_passo_atual]
        estado_seguinte = self.automato_caminho_puzzle[self.automato_passo_atual + 1]
        
        def proximo_passo_callback():
            self.automato_passo_atual += 1
            self.executar_passo_automato_fixo()

        self.animar_passo_generico(
            estado_anterior, estado_seguinte,
            canvas=self.canvas_animacao_automato,
            callback=proximo_passo_callback
        )

    def atualizar_info_automato_fixo(self):
        passo = self.automato_passo_atual
        
        fita_texto = " ".join(self.automato_fita)
        self.label_fita.config(text=f"Fita:       {fita_texto}")

        if passo < len(self.automato_fita):
            cabecote_pos = passo * 2
            cabecote_texto = (" " * cabecote_pos) + "↑"
            self.label_cabecote.config(text=f"Cabeçote:   {cabecote_texto}")
        else:
            self.label_cabecote.config(text="Cabeçote:")

        estado_atual = self.automato_estados[passo]
        self.label_controle.config(text=f"Controle:   {estado_atual}")

        if self.automato_animacao_em_curso and passo < len(self.automato_fita):
            simbolo_lido = self.automato_fita[passo]
            proximo_estado = self.automato_estados[passo + 1]
            transicao_texto = f"δ({estado_atual}, {simbolo_lido}) = {proximo_estado}"
            self.label_transicao.config(text=f"Transição: {transicao_texto}")
        else:
            self.label_transicao.config(text="Transição: -")

    def desenhar_diagrama_automato_fixo(self):
        canvas = self.canvas_diagrama_automato
        canvas.delete("all")
        
        width, height = canvas.winfo_width(), canvas.winfo_height()
        if width < 50 or height < 50: return

        num_nodes = len(self.automato_estados)
        padding_x, padding_y = width * 0.10, height * 0.5
        x_step = (width - 2 * padding_x) / (num_nodes - 1)
        node_radius = min(width * 0.035, height * 0.15, 25)

        posicoes = {estado: (padding_x + i * x_step, padding_y) for i, estado in enumerate(self.automato_estados)}

        for i, estado_origem in enumerate(self.automato_estados[:-1]):
            simbolo = self.automato_fita[i]
            x1, y1 = posicoes[estado_origem]
            x2, y2 = posicoes[self.automato_estados[i+1]]
            
            is_active_transition = (i == self.automato_passo_atual) and self.automato_animacao_em_curso
            cor = "red" if is_active_transition else "darkgreen"
            largura = 3 if is_active_transition else 1.5

            canvas.create_line(x1 + node_radius, y1, x2 - node_radius, y2, arrow=tk.LAST, fill=cor, width=largura)
            canvas.create_text((x1+x2)/2, y1 - 25, text=simbolo, font=("Arial", 12, "italic"), fill=cor)

        for i, estado in enumerate(self.automato_estados):
            x, y = posicoes[estado]
            is_active_state = (i == self.automato_passo_atual) or \
                                (self.automato_animacao_em_curso and i == self.automato_passo_atual + 1)
            
            cor_borda = "red" if is_active_state else "black"
            cor_fundo = "gold" if is_active_state else "lightblue"
            largura = 3 if is_active_state else 2

            canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, 
                                    fill=cor_fundo, outline=cor_borda, width=largura)
            canvas.create_text(x, y, text=estado, font=("Arial", 14, "bold"))

    def _load_images(self):
        try:
            for key, visual in self.item_visuals.items():
                img = Image.open(visual["arquivo"])
                img = img.resize(visual["size"], Image.Resampling.LANCZOS)
                self.loaded_images[key] = ImageTk.PhotoImage(img)
            
            barco_img = Image.open("assets/barco.png")
            barco_img = barco_img.resize((150, 100), Image.Resampling.LANCZOS)
            self.loaded_images["barco"] = ImageTk.PhotoImage(barco_img)
        except FileNotFoundError as e:
            messagebox.showerror("Arquivo não encontrado", f"Não foi possível encontrar: {e.filename}\nCertifique-se que as imagens (.png) estão na pasta 'assets'.")
            self.destroy()

    def _get_movimento_label(self, estado_anterior, estado_atual, item_map):
        destino_char = estado_atual[0]
        destino = "Direita" if destino_char == 'D' else "Esquerda"
        item_movido = "sozinho"
        for item, index in item_map.items():
            if estado_anterior[index] != estado_atual[index]:
                item_movido = item
                break
        
        simbolo_acao = ''
        if item_movido == "cabra": simbolo_acao = '(a)'
        if item_movido == "sozinho": simbolo_acao = '(b)'
        if item_movido == "lobo": simbolo_acao = '(c)'
        if item_movido == "repolho": simbolo_acao = '(d)'
        
        if item_movido == "sozinho":
            return f"{simbolo_acao} Fazendeiro volta sozinho para a margem {destino}"
        else:
            return f"{simbolo_acao} Leva o(a) {item_movido} para a margem {destino}"

    def resolver_e_preparar(self):
        self.canvas_grafo.delete("all")
        self.notebook_visualizacao.tab(1, state="disabled")
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

        self.grafo_caminho_data = self.caminho_solucao
        self.grafo_item_map_data = automato.item_map
        self._desenhar_solucao_grafo()

        self.preparar_animacao()
        self.notebook_visualizacao.tab(1, state="normal")
        self.notebook_visualizacao.select(1)
        self.start_anim_button.config(state="normal")
        self.reset_anim_button.config(state="normal")

    def _on_resize_grafo(self, event):
        if self._job_id_grafo:
            self.after_cancel(self._job_id_grafo)
        self._job_id_grafo = self.after(150, self._desenhar_solucao_grafo)

    def _desenhar_solucao_grafo(self):
        self.canvas_grafo.delete("all")
        if not self.grafo_caminho_data: return

        caminho = self.grafo_caminho_data
        item_map, width, height = self.grafo_item_map_data, self.canvas_grafo.winfo_width(), self.canvas_grafo.winfo_height()
        if width < 50 or height < 50: return

        nodes_per_row = 4
        padding_x, padding_y = width * 0.12, height * 0.15
        
        num_rows = math.ceil(len(caminho) / nodes_per_row)
        x_step = (width - 2 * padding_x) / (nodes_per_row - 1) if nodes_per_row > 1 else 0
        y_step = (height - 2 * padding_y) / (num_rows - 1) if num_rows > 1 else height / 2
        node_radius = min(width * 0.03, height * 0.04, 30)
        posicoes_nos = {} 

        for i, estado in enumerate(caminho):
            row, col = i // nodes_per_row, i % nodes_per_row
            x = (padding_x + col * x_step) if row % 2 == 0 else (width - padding_x - col * x_step)
            y = (padding_y + row * y_step) if num_rows > 1 else padding_y
            posicoes_nos[i] = (x, y)

        for i, estado in enumerate(caminho):
            if i > 0:
                px, py = posicoes_nos[i-1]
                x, y = posicoes_nos[i]
                self.canvas_grafo.create_line(px, py, x, y, arrow=tk.LAST, fill="darkgreen", width=1.5)
                label_x, label_y = (px + x) / 2, (py + y) / 2 - 15
                movimento = self._get_movimento_label(caminho[i-1], estado, item_map).split(" para")[0]
                text_id = self.canvas_grafo.create_text(label_x, label_y, text=movimento, font=("Arial", 10, "italic"), fill="darkgreen")
                bbox = self.canvas_grafo.bbox(text_id)
                self.canvas_grafo.create_rectangle(bbox, fill="white", outline="")
                self.canvas_grafo.tag_raise(text_id)

        for i, estado in enumerate(caminho):
            x, y = posicoes_nos[i]
            self.canvas_grafo.create_oval(x-node_radius, y-node_radius, x+node_radius, y+node_radius, fill="lightblue", outline="black", width=2)
            self.canvas_grafo.create_text(x, y - node_radius - 15, text=f"q{i}", font=("Arial", 14, "bold"))
            self.canvas_grafo.create_text(x, y + node_radius + 20, text=str(estado), font=("Arial", 10), fill="black")

    def _on_resize_animacao(self, event):
        if self.animacao_em_curso: return
        if self._job_id_animacao:
            self.after_cancel(self._job_id_animacao)
        self._job_id_animacao = self.after(150, self._redraw_canvas_animacao)

    def _redraw_canvas_animacao(self):
        if not self.caminho_solucao: return
        self.canvas_animacao.delete("all")
        self._desenhar_cenario_animacao(self.canvas_animacao)
        self.desenhar_estado_animacao(self.caminho_solucao[self.passo_atual_animacao], self.canvas_animacao)

    def _desenhar_cenario_animacao(self, canvas):
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 2 or h < 2: return

        for i in range(int(h * 0.7)):
            r, g, b = 135 + int(90 * i / (h * 0.7)), 206 + int(40 * i / (h * 0.7)), 250
            canvas.create_line(0, i, w, i, fill=f'#{r:02x}{g:02x}{b:02x}')
        
        canvas.create_oval(w*0.8, h*0.1, w*0.9, h*0.25, fill="#FFD700", outline="#FFA500")
        canvas.create_oval(w*0.1, h*0.15, w*0.25, h*0.3, fill="white", outline="")
        canvas.create_oval(w*0.18, h*0.1, w*0.3, h*0.25, fill="white", outline="")

        for i in range(int(h * 0.7), h):
            b = 180 - int(90 * (i - h * 0.7) / (h * 0.3))
            canvas.create_line(0, i, w, i, fill=f'#4682{b:02x}')

        margem_esq_x_fim, margem_dir_x_inicio = w * 0.25, w * 0.75
        nivel_grama = max(h - 120, h * 0.6)

        canvas.create_rectangle(0, nivel_grama, margem_esq_x_fim, h, fill="#A0522D", outline="#6B4226", width=2)
        canvas.create_rectangle(margem_dir_x_inicio, nivel_grama, w, h, fill="#A0522D", outline="#6B4226", width=2)
        canvas.create_rectangle(0, nivel_grama, margem_esq_x_fim, nivel_grama + 10, fill="#228B22", outline="")
        canvas.create_rectangle(margem_dir_x_inicio, nivel_grama, w, nivel_grama + 10, fill="#228B22", outline="")
        canvas.create_text(margem_esq_x_fim / 2, nivel_grama + 40, text="MARGEM ESQUERDA", font=("Arial", 12, "bold"), fill="white")
        canvas.create_text(margem_dir_x_inicio + (w-margem_dir_x_inicio)/2, nivel_grama + 40, text="MARGEM DIREITA", font=("Arial", 12, "bold"), fill="white")
    
    def preparar_animacao(self):
        if self.animacao_em_curso: return
        self.passo_atual_animacao = 0
        self._redraw_canvas_animacao()
        self.start_anim_button.config(state="normal")

    def desenhar_estado_animacao(self, estado, canvas):
        canvas.delete("personagem")
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 2 or h < 2: return

        margem_esq_x_fim, margem_dir_x_inicio = w * 0.25, w * 0.75
        nivel_grama = max(h - 120, h * 0.6)

        mapa_estado = {"fazendeiro": estado[0], "lobo": estado[1], "cabra": estado[2], "repolho": estado[3]}
        itens_esquerda = [item for item, pos in mapa_estado.items() if pos == 'E']
        itens_direita = [item for item, pos in mapa_estado.items() if pos == 'D']

        y_pos, x_spacing = nivel_grama - 25, 65

        for key in self.item_visuals: self.item_visuals[key]["id"] = None
        
        if itens_esquerda:
            start_x = (margem_esq_x_fim / 2) - (len(itens_esquerda) - 1) * x_spacing / 2
            for i, key in enumerate(itens_esquerda):
                self.item_visuals[key]["id"] = canvas.create_image(start_x + i * x_spacing, y_pos, image=self.loaded_images[key], tags="personagem")

        if itens_direita:
            start_x = (margem_dir_x_inicio + w) / 2 - (len(itens_direita) - 1) * x_spacing / 2
            for i, key in enumerate(itens_direita):
                self.item_visuals[key]["id"] = canvas.create_image(start_x + i * x_spacing, y_pos, image=self.loaded_images[key], tags="personagem")

    def iniciar_animacao(self):
        if self.animacao_em_curso: return
        self.animacao_em_curso = True
        self.solve_button.config(state="disabled")
        self.start_anim_button.config(state="disabled")
        self.reset_anim_button.config(state="disabled")
        self.animar_passo()

    def animar_passo(self):
        if self.passo_atual_animacao >= len(self.caminho_solucao) - 1:
            self.canvas_animacao.delete("acao_texto") 
            
            self.canvas_animacao.create_text(
                self.winfo_width() / 2, 50, 
                text="Travessia Concluída! Parabéns!", 
                font=("Arial", 22, "bold"), 
                fill="#32CD32", 
                tags="fim_msg"
            )
            self.animacao_em_curso = False
            self.solve_button.config(state="normal")
            self.reset_anim_button.config(state="normal")
            return

        estado_anterior = self.caminho_solucao[self.passo_atual_animacao]
        estado_seguinte = self.caminho_solucao[self.passo_atual_animacao + 1]
        
        def proximo_passo_callback():
            self.passo_atual_animacao += 1
            self.after(800, self.animar_passo)

        self.animar_passo_generico(estado_anterior, estado_seguinte, self.canvas_animacao, proximo_passo_callback)

    def animar_passo_generico(self, estado_anterior, estado_seguinte, canvas, callback):
        canvas.delete("acao_texto", "fim_msg")
        
        passageiro_key = next((item for item, index in AutomatoTravessia().item_map.items() if estado_anterior[index] != estado_seguinte[index]), None)
        
        w, h = canvas.winfo_width(), canvas.winfo_height()
        margem_esq_x_fim, margem_dir_x_inicio = w * 0.25, w * 0.75
        nivel_grama = max(h - 120, h * 0.6)
        y_barco = nivel_grama - 40
        
        direcao_de = estado_anterior[0]
        x_partida = margem_esq_x_fim + 75 if direcao_de == 'E' else margem_dir_x_inicio - 75
        x_chegada = margem_dir_x_inicio - 75 if direcao_de == 'E' else margem_esq_x_fim + 75
        
        label_movimento = self._get_movimento_label(estado_anterior, estado_seguinte, AutomatoTravessia().item_map)
        canvas.create_text(w/2, 50, text=label_movimento, font=("Arial", 16, "italic"), fill="black", tags="acao_texto")

        self.id_barco = canvas.create_image(x_partida, y_barco, image=self.loaded_images["barco"], tags="barco")
        
        for key, offset_x in [("fazendeiro", -15), (passageiro_key, 25)]:
            if key and self.item_visuals[key].get("id"):
                item_id = self.item_visuals[key]["id"]
                try:
                    ix, iy = canvas.coords(item_id)
                    canvas.move(item_id, x_partida - ix + offset_x, y_barco - iy + 5)
                    canvas.tag_raise(item_id)
                except tk.TclError: pass

        self.movimento_suave_generico(canvas, x_chegada - x_partida, 0, passageiro_key, estado_seguinte, callback)

    def movimento_suave_generico(self, canvas, dx, dy, passageiro_key, estado_final, callback, passos=120, passo_atual=0):
        if passo_atual < passos:
            movimento_x = dx / passos
            movimento_y = math.sin(passo_atual * math.pi / (passos / 2)) * 0.15

            canvas.move(self.id_barco, movimento_x, movimento_y)
            if self.item_visuals["fazendeiro"].get("id"): canvas.move(self.item_visuals["fazendeiro"]["id"], movimento_x, movimento_y)
            if passageiro_key and self.item_visuals[passageiro_key].get("id"): canvas.move(self.item_visuals[passageiro_key]["id"], movimento_x, movimento_y)
            
            self.after(20, lambda: self.movimento_suave_generico(canvas, dx, dy, passageiro_key, estado_final, callback, passos, passo_atual + 1))
        else:
            canvas.delete(self.id_barco)
            self.desenhar_estado_animacao(estado_final, canvas)
            self.after(500, callback)

if __name__ == "__main__":
    app = TravessiaApp()
    app.mainloop()