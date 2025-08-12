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
            # Esta verificação é uma salvaguarda. A validação principal é feita no main.
            raise ValueError(f"O estado inicial fornecido {estado_inicial} é inválido e viola as regras.")
            
        # q₀ (Estado Inicial): (Fazendeiro, Lobo, Cabra, Repolho)
        self.estado_inicial = estado_inicial

        # F (Estado Final)
        self.estado_final = ('D', 'D', 'D', 'D')

        # Σ (Alfabeto de Entrada / Ações)
        self.alfabeto = ["lobo", "cabra", "repolho", "sozinho"]
        self.item_map = {"lobo": 1, "cabra": 2, "repolho": 3}

    def is_valid_state(self, estado):
        """
        Verifica se um estado viola alguma regra do problema.
        Retorna False se o estado for inválido.
        """
        _fazendeiro, lobo, cabra, repolho = estado

        # Regra 1: Lobo não pode ficar sozinho com a cabra.
        if lobo == cabra and _fazendeiro != lobo:
            return False

        # Regra 2: Cabra não pode ficar sozinha com o repolho.
        if cabra == repolho and _fazendeiro != cabra:
            return False

        return True

    def transition(self, estado_atual, acao):
        """
        δ (Função de Transição): Calcula o próximo estado dado um estado e uma ação.
        Retorna o novo estado se a transição for válida, senão retorna None.
        """
        fazendeiro_pos = estado_atual[0]
        
        if acao != "sozinho":
            item_index = self.item_map[acao]
            if estado_atual[item_index] != fazendeiro_pos:
                return None

        proxima_pos_fazendeiro = 'D' if fazendeiro_pos == 'E' else 'E'
        proximo_estado = list(estado_atual)
        proximo_estado[0] = proxima_pos_fazendeiro
        
        if acao != "sozinho":
            proximo_estado[self.item_map[acao]] = proxima_pos_fazendeiro

        proximo_estado_tupla = tuple(proximo_estado)
        
        if self.is_valid_state(proximo_estado_tupla):
            return proximo_estado_tupla
        else:
            return None

    def resolver_bfs(self):
        """
        Usa o algoritmo de Busca em Largura (BFS) para encontrar o caminho mais curto.
        """
        if self.estado_inicial == self.estado_final:
            return [[self.estado_inicial]]
            
        fila = deque([[self.estado_inicial]])
        visitados = {self.estado_inicial}

        while fila:
            caminho_atual = fila.popleft()
            ultimo_estado = caminho_atual[-1]

            if ultimo_estado == self.estado_final:
                return caminho_atual

            for acao in self.alfabeto:
                novo_estado = self.transition(ultimo_estado, acao)
                
                if novo_estado and novo_estado not in visitados:
                    visitados.add(novo_estado)
                    novo_caminho = list(caminho_atual)
                    novo_caminho.append(novo_estado)
                    fila.append(novo_caminho)
        
        return None

    def imprimir_solucao(self, caminho):
        """
        Imprime a solução encontrada de forma legível.
        """
        if not caminho:
            print("\n>> Não foi encontrada uma solução a partir do estado fornecido.")
            return

        print("\n Solução Encontrada para o Problema da Travessia")
        print(f"Estado Inicial: {caminho[0]}")
        print("-" * 55)

        # Se o caminho tem apenas um estado, significa que já começou no estado final.
        if len(caminho) == 1:
            print("O estado inicial já é o estado final. Sem travessias a fazer.")
        else:
            for i in range(len(caminho) - 1):
                estado_anterior = caminho[i]
                estado_atual = caminho[i+1]
                
                origem = 'esquerda' if estado_anterior[0] == 'E' else 'direita'
                destino = 'direita' if estado_atual[0] == 'D' else 'esquerda'
                
                item_movido = "sozinho"
                for item, index in self.item_map.items():
                    if estado_anterior[index] != estado_atual[index]:
                        item_movido = item
                        break
                
                print(f"Passo {i+1}: Fazendeiro atravessa da {origem} para {destino} levando o/a {item_movido}")
                print(f"   Novo estado das margens: {estado_atual}")
        
        print("-" * 55)
        print("Todos chegaram à margem direita em segurança")


def main():
    """
    Função principal para interagir com o usuário e executar o programa.
    """
    while True:
        print("\nInsira o estado inicial no formato: F L C R")
        print("Onde F=Fazendeiro, L=Lobo, C=Cabra, R=Repolho.")
        try:
            entrada_usuario = input("Digite o estado inicial: ").strip().upper()
        except KeyboardInterrupt:
            sys.exit()

        partes = entrada_usuario.split()

        # Validação do formato da entrada
        if len(partes) != 4 or not all(p in ['E', 'D'] for p in partes):
            print("\nFormato inválido. Insira 4 valores ('E' ou 'D') separados por espaço")
            continue
        
        estado_inicial_usuario = tuple(partes)
        
        # Validação das regras do jogo para o estado inicial
        # É preciso criar uma instância temporária para usar o método de validação
        if not AutomatoTravessia().is_valid_state(estado_inicial_usuario):
            print(f"\nO estado inicial '{estado_inicial_usuario}' viola as regras do problema.")
            print("O lobo não pode ficar com a cabra, e a cabra não pode ficar com o repolho, a menos que o fazendeiro esteja junto.")
            continue

        # Se a entrada é válida, cria o autômato e tenta resolver
        try:
            automato = AutomatoTravessia(estado_inicial=estado_inicial_usuario)
            caminho_solucao = automato.resolver_bfs()
            automato.imprimir_solucao(caminho_solucao)
            break # Encerra o loop após encontrar a solução
        except ValueError as e:
            # Captura o erro do __init__ como uma segurança extra
            print(f"\n[ERRO] {e}")


if __name__ == "__main__":
    main()