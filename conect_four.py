import os
import random
import math
import csv
from collections import defaultdict

# PRIO TODO: Implementar árvore de decisão ID3 e tratar dos dataset's e BD.

#Refatorar uct_search, não há cálculo das estatísticas dos nós (Ver slides UCB1) - DONE
#implementação ta em jogador vs computador ,falta implementar jogador vs jogador e computador vs computador - DONE
#as regras do jogo não estão implementadas como deveriam,pode ser visto no tableaux apresentado quando o codigo é executado - DONE
#falta melhorar diversas coisas no codigo ,como testar diferentes parâmetros para o UCT(numeros de simulações filhos por nós), e melhorar a interface gráfica - DONE
#integrar o jogo para o modo humano vs computador : o computador deve tomar decisões inteligentes e não aleatórias contra o jogador humano - (Há um problema na implementação do uct_search - Não é calculado o UCB1) - DONE
#usar mcts para gerar estados do jogo e as melhores jogadas ,salvar esses dados como um dataset(cs.. ou json) - DONE
#cenarios do jogo,humano vs humano ,humano vs computador,computador vs computador (compare os metodos ) - DONE

#de seguida as melhorias devemos tratar do dataset para arvore de decisão (ID3) para o treino do modelo 
#falta implementar a arvore de decisão e o dataset para treino do modelo
#falta implementar a função para testar novas jogadas usando a arvore de decisão
#melhorar eficiência do código e torna-lo mais agil para o usuario
#criar banco de dados para treinar a arvore de decisão(não usar sckit learn ,ta escrito no enunciado)
#criar função para testar novas jogadas usando a arvore,o computador deve tomar decisões baseadas na arvore de decisão
#vejam  o codigo por inteiro por favor e comentem o que acham que deve ser melhorado ou adicionado,o que esta errado

#emojis unicode: https://unicode.org/emoji/charts/full-emoji-list.html (trocar '+' por 000)

def create_board():
    board = []
    for _ in range(6):
        board.append(["_"]*7)
    return board

def print_board(board):
    #os.system('clear' if os.name == 'posix' else 'cls')      #<<<----- comentar essa linha antes de executar para ver o tableaux
    print(" 0 1 2 3 4 5 6")
    for row in board:
        print("|" + "|".join(row) + "|")
    print()

def human_vs_human(state):
    os.system('clear' if os.name == 'posix' else 'cls')
    while not state.is_terminal():
        print_board(state.board)
        current_player = state.current_player
        while True:
            try:
                col = int(input(f"Player {state.current_player}, choose column (0-6): "))
                if 0 <= col <= 6 and not state.is_column_full(col):
                    new_state = state.do_move(col)
                    if new_state:
                        state = new_state
                        break
                print("Invalid move. Column full or out of range.")
            except ValueError:
                print("Please enter a number between 0 and 6.")
    
    print_board(state.board)
    print_result(state)

def human_vs_pc(state):
    while not state.is_terminal():
        os.system('clear' if os.name == 'posix' else 'cls')
        print_board(state.board)
        if state.current_player == 'X':
            print("X Joga:\n")
            move = get_human_move(state)
        else:
            print("O Joga:\n")
            move = uct_search(state, 1000)
        state = state.do_move(move)
    
    print_board(state.board)
    print_result(state)

def pc_vs_pc(state):
    while not state.is_terminal():
        os.system('clear' if os.name == 'posix' else 'cls')
        print_board(state.board)
        if state.current_player == 'X':
            print(f"MCTS (X) Plays:\n")
            move = uct_search(state, 1000)
        else:
            print(f"ID3 (O) Plays:\n")
            move = id3_procedure(state)
        state = state.do_move(move)
        os.system('sleep 1')

    print_board(state.board)
    print_result(state)

### Função para o ID3 - Martim

# Funções para extração de features e análise do tabuleiro
def converter_state_para_board(state_str):
    return [list(state_str[i*7:(i+1)*7]) for i in range(6)]

def extrair_diagonais(board):
    diagonais = []
    # Diagonais principais
    for i in range(-2, 4):
        diag = [board[row][row+i] for row in range(6) if 0 <= row+i < 7]
        if len(diag) >= 4:
            diagonais.append(diag)
    # Diagonais secundárias
    for i in range(3, 9):
        diag = [board[row][i-row] for row in range(6) if 0 <= i-row < 7]
        if len(diag) >= 4:
            diagonais.append(diag)
    return diagonais

def verificar_padrao(window, prefix):
    patterns = {
        'X3': ['X','X','X','_'],
        '_XXX': ['_','X','X','X'],
        'O3': ['O','O','O','_'],
        '_OOO': ['_','O','O','O'],
        'XX_X': ['X','X','_','X'],
        'OO_O': ['O','O','_','O']
    }
    found = {}
    for name, pattern in patterns.items():
        if window == pattern:
            found[f'{prefix}_{name}'] = 1
    return found

def analisar_ameacas(board):
    threats = {}
    for row in range(6): # Varredura horizontal
        for col in range(4):
            window = [board[row][col+i] for i in range(4)]
            threats.update(verificar_padrao(window, f'h{row}{col}'))
    
    for col in range(7): # Varredura vertical
        for row in range(3):
            window = [board[row+i][col] for i in range(4)]
            threats.update(verificar_padrao(window, f'v{col}{row}'))
    
    diagonais = extrair_diagonais(board) # Varredura diagonal
    for i, diag in enumerate(diagonais):
        for j in range(len(diag)-3):
            window = diag[j:j+4]
            threats.update(verificar_padrao(window, f'd{i}{j}'))
    
    return threats

def analisar_potencias(board):
    potencias = {}
    for col in [2,3,4]:
        potencias[f'col{col}_x'] = sum(1 for row in range(6) if board[row][col] == 'X')
        potencias[f'col{col}_o'] = sum(1 for row in range(6) if board[row][col] == 'O')
    for row in range(6):
        x_count = board[row].count('X')
        o_count = board[row].count('O')
        if x_count >= 2: potencias[f'row{row}_x'] = x_count
        if o_count >= 2: potencias[f'row{row}_o'] = o_count
    return potencias

def extrair_features(state_str):
    board = converter_state_para_board(state_str)
    features = {}
    features['centro'] = sum(1 for col in [2,3,4] if board[0][col] == '_')
    features.update(analisar_ameacas(board))
    features.update(analisar_potencias(board))
    return features

class ID3DecisionTree:
    def __init__(self):
        self.tree = {}
        self.feature_list = []

    def train(self, dataset):
        # Processamento do dataset para extração de features
        processed_data = []
        for row in dataset:
            state_str = row['state']
            features = extrair_features(state_str)
            features['move'] = int(row['move']) if row['move'].isdigit() else 0
            processed_data.append(features)

        if not processed_data:
            return
            
        self.feature_list = list(processed_data[0].keys())
        self.feature_list.remove('move')
        self.tree = self.construir_arvore(processed_data, self.feature_list.copy())

    def construir_arvore(self, data, features, depth=0):
        #Condições de parada
        if not data or depth > 5:  # Limitar profundidade máxima
            return self.obter_movimento_mais_comum(data)
        
        moves = set(d['move'] for d in data) #Verificar se todos os exemplos têm o mesmo movimento
        if len(moves) == 1:
            return next(iter(moves))

        best_feature = self.selecionar_melhor_feature(data, features) #Selecionar melhor feature
        if not best_feature:
            return self.obter_movimento_mais_comum(data)
        
        node = {best_feature: {}} #Construir nó da árvore
        remaining_features = [f for f in features if f != best_feature]
        feature_values = set(d.get(best_feature, None) for d in data) #construir subárvores para cada valor da feature
        for value in feature_values:
            subset = [d for d in data if d.get(best_feature) == value]
            if subset:
                node[best_feature][value] = self.construir_arvore(subset, remaining_features, depth+1)
        
        return node

    def selecionar_melhor_feature(self, data, features):
        best_gain = -1
        best_feature = None
        entropy_total = self.calcular_entropia(data)
        
        for feature in features:
            gain = self.calcular_ganho(data, feature, entropy_total)
            if gain > best_gain:
                best_gain = gain
                best_feature = feature
        return best_feature

    def calcular_entropia(self, data):
        if not data:
            return 0
        counts = defaultdict(int)
        for d in data:
            counts[d['move']] += 1
        total = len(data)
        return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)

    def calcular_ganho(self, data, feature, entropy_total):
        values = defaultdict(list)
        for d in data:
            values[d.get(feature)].append(d['move'])
        
        weighted_entropy = 0
        total = len(data)
        for value, moves in values.items():
            subset_entropy = self.calcular_entropia([{'move': m} for m in moves])
            weighted_entropy += (len(moves)/total) * subset_entropy
        
        return entropy_total - weighted_entropy

    def obter_movimento_mais_comum(self, data):
        if not data:
            return random.randint(0, 6)
        counts = defaultdict(int)
        for d in data:
            counts[d['move']] += 1
        return max(counts, key=counts.get)

    def predict(self, state):
        current_state = ''.join([''.join(row) for row in state.board])
        features = extrair_features(current_state)
        legal_moves = state.get_legal_moves()
        
        def navegar(node):
            if not isinstance(node, dict):
                return node
            feature = next(iter(node))
            value = features.get(feature, None)
            if value not in node[feature]:
                return self.obter_movimento_mais_comum([])
            return navegar(node[feature][value])
    
        move = navegar(self.tree)
        return move if move in legal_moves else random.choice(legal_moves)

id3_tree = ID3DecisionTree()

def id3_procedure(state):
    state_str = ''.join([''.join(row) for row in state.board])
    features = extrair_features(state_str)
    legal_moves = state.get_legal_moves()
    move = id3_tree.predict(state)
    return move if move in legal_moves else random.choice(legal_moves)


def iniciar_id3():
    global id3_tree
    if not id3_tree.tree:
        if not os.path.exists('MCTS_dataset.csv'):
            generateDataset()
        print("Carregando dataset para treinar a árvore ID3...")
        with open('MCTS_dataset.csv') as f:
            reader = csv.DictReader(f)
            dataset = list(reader)
        print("Treinando árvore de decisão...")
        id3_tree.train(dataset)
        print("Treinamento concluído!")
    
def simulate_pc_vs_pc(n=1):
    results = {'X': 0, 'O': 0, 'Draw': 0}
    for _ in range(n):
        state = ConnectFourState()
        while not state.is_terminal():
            if state.current_player == 'X':
                move = uct_search(state, 300)  # Computador X usa MCTS
            else:
                move = id3_procedure(state)  # Computador O usa ID3
            state = state.do_move(move)
        winner = state.get_winner()
        if winner == 1:
            results['X'] += 1
        elif winner == -1:
            results['O'] += 1
        else:
            results['Draw'] += 1
    os.system('clear' if os.name == 'posix' else 'cls')
    print(results)

### MARTIM TERMINA EXPLICAÇÃO

def get_human_move(state):
    while True:
        try:
            col = int(input(f"Jogador {state.current_player}, escolha uma coluna (0-6): "))
            if 0 <= col <= 6 and not state.is_column_full(col):
                return col
            print("Movimento inválido. Coluna cheia ou índice fora de alcance.")
        except ValueError:
            print("Por favor digite um número entre 0 e 6.")

def print_result(state):
    winner = state.get_winner()
    if winner == 1:
        print("X wins!")
    elif winner == -1:
        print("O wins!")
    else:
        print("Draw!")

class ConnectFourState:
    def __init__(self):
        self.board = create_board()
        self.current_player = 'X'
        self.last_move = None
    
    def clone(self):
        new_state = ConnectFourState()
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.last_move = self.last_move
        return new_state
    
    def get_legal_moves(self):
        return [col for col in range(7) if not self.is_column_full(col)]
    
    def is_column_full(self, col):
        return self.board[0][col] != '_'
    
    def do_move(self, col):
        if col < 0 or col > 6 or self.is_column_full(col):
            return None
        new_state = self.clone()

        # Encontrar a posição vazia mais baixa na coluna
        for row in range(5, -1, -1):
            if new_state.board[row][col] == '_':
                new_state.board[row][col] = self.current_player
                new_state.last_move = (row, col)
                new_state.current_player = 'O' if self.current_player == 'X' else 'X'
                return new_state
        return None

    def is_terminal(self):
        return self.get_winner() is not None or len(self.get_legal_moves()) == 0

    def get_winner(self):
        directions = [
            (0, 1),  # horizontal
            (1, 0),  # vertical
            (1, 1),  # diagonal baixo-direita
            (1, -1)  # diagonal baixo-esquerda
        ]
        
        for row in range(6):
            for col in range(7):
                if self.board[row][col] == '_':
                    continue
                    
                for dr, dc in directions:
                    # Verificar se há 4 peças iguais na direção
                    try:
                        if (self.board[row][col] == self.board[row + dr][col + dc] ==
                            self.board[row + 2*dr][col + 2*dc] == 
                            self.board[row + 3*dr][col + 3*dc] != '_'):
                            return 1 if self.board[row][col] == 'X' else -1
                    except IndexError:
                        continue
        return None

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_value = 0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_moves())
    
    def select_child(self):
        exploration_constant = math.sqrt(2)
        
        # Função para calcular o valor UCB1
        def ucb_value(child):
            exploitation = child.total_value / child.visits if child.visits > 0 else float('inf')
            exploration = exploration_constant * math.sqrt(math.log(self.visits) / child.visits) if child.visits > 0 else float('inf')
            return exploitation + exploration
            
        return max(self.children, key=ucb_value)

    def add_child(self, child_state):
        child = Node(child_state, self)
        self.children.append(child)
        return child

def uct_search(state, num_iterations):
    root_node = Node(state)
    
    for i in range(num_iterations):
        node = root_node
        current_state = state.clone()
        
        # Selection
        while not current_state.is_terminal() and node.is_fully_expanded():
            node = node.select_child()
            current_state = current_state.do_move(node.state.last_move[1])
        
        # Expansion
        if not current_state.is_terminal():
            explored_moves = set()
            for child in node.children:
                if child.state.last_move:
                    explored_moves.add(child.state.last_move[1])
                    
            unexplored_moves = [m for m in current_state.get_legal_moves() if m not in explored_moves]
            
            if unexplored_moves:
                chosen_move = random.choice(unexplored_moves)
                current_state = current_state.do_move(chosen_move)
                node = node.add_child(current_state)
        
        # Simulation
        simulation_state = current_state.clone()
        while not simulation_state.is_terminal():
            legal_moves = simulation_state.get_legal_moves()
            move = random.choice(legal_moves)
            simulation_state = simulation_state.do_move(move)
        
        # Backpropagation
        result = simulation_state.get_winner()
        while node is not None:
            node.visits += 1
            
            if result is not None:
                # Calcular valor do nó baseado no resultado e no jogador atual
                if (result == 1 and node.state.current_player == 'O') or \
                   (result == -1 and node.state.current_player == 'X'):
                    node_value = 1  # Vitória para o jogador que fez o movimento
                else:
                    node_value = -1  # Derrota para o jogador que fez o movimento
            else:
                node_value = 0  # Empate
                
            node.total_value += node_value
            node = node.parent
    
    # Escolher o movimento com mais visitas (mais robusto que maior valor)
    if root_node.children:
        best_child = max(root_node.children, key=lambda c: c.visits)
        return best_child.state.last_move[1]
    else:
        return random.choice(state.get_legal_moves())

def show_menu():
    print("\n" + "="*38)
    print("     CONNECT FOUR - Modos de Jogo")
    print("="*38)
    print("1. Humano vs Humano (\U0001F464 x \U0001F464)")
    print("2. Humano vs Computador (\U0001F464 x \U0001F916)")
    print("3. Computador vs Computador (\U0001F916 x \U0001F916)")
    print("4. Múltiplas amostras PCvsPC (\U0001F916\U0001F916\U0001F916 x \U0001F916\U0001F916\U0001F916)")
    print("5. Sair")
    print("="*38)

def generateDataset(num_games=100, iterations_per_move=1000, filename='MCTS_dataset.csv'):
    if os.path.exists(filename):
        print(f"Dataset existente encontrado em {filename}, delete {filename} e execute novamente se quiser usar um novo dataset")
        return
    
    print(f"Gerando novo dataset com {num_games} jogos e {iterations_per_move} iterações...")
    dataset = []
    for _ in range(num_games):
        state = ConnectFourState()
        while not state.is_terminal():
            board_state = ''.join([''.join(row) for row in state.board])
            best_move = uct_search(state, iterations_per_move)
            dataset.append({'state': board_state, 'move': best_move})
            state = state.do_move(best_move)

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['state', 'move']
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        writer.writerows(dataset)
    return dataset

def main():
    iniciar_id3()
    while True:
        show_menu()
        try:
            choice = int(input("ESCOLHER MODO DE JOGO (1-4): "))
            if 1 <= choice <= 5:
                state = ConnectFourState()
                if choice == 1:
                    human_vs_human(state)
                elif choice == 2:
                    human_vs_pc(state)
                elif choice == 3:
                    pc_vs_pc(state)
                elif choice == 4:
                    simulate_pc_vs_pc(10)
                elif choice == 5:
                    print("Saindo do jogo. Até logo!")
                    break
            else:
                os.system('clear' if os.name == 'posix' else 'cls')
                print("\nOpção inválida. Tente novamente.\n")
        except ValueError:
            print("\nPor favor insira um número entre 1 e 4:\n")

if __name__ == "__main__":
    main()