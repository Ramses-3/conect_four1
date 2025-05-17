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
            move = id3_procedure(state) #Integrar ID3 ao código aqui
        state = state.do_move(move)
        os.system('sleep 1')

    print_board(state.board)
    print_result(state)

id3_test_tree = {}

def id3_procedure(state):
    flat = [cell for row in state.board for cell in row]
    board = [flat[i*7:(i+1)*7] for i in range(6)]
    features = {f'cell_{i}': flat[i] for i in range(42)}
    features.update(extrair_features(board))
    legal_moves = state.get_legal_moves()
    move = predict_with_tree(id3_test_tree, features)
    return move if isinstance(move, int) and move in legal_moves else random.choice(legal_moves)

def extrair_features(board):
    features = {}
    for col in range(7):
        col_vals = [board[row][col] for row in range(6)]
        features[f'count_X_col_{col}'] = col_vals.count('X')
        features[f'count_O_col_{col}'] = col_vals.count('O')
        features[f'count__col_{col}'] = col_vals.count('_')
        features[f'top_{col}'] = next((cell for cell in col_vals if cell != '_'), '_')
    return features

def predict_with_tree(tree, example):
    while isinstance(tree, dict):
        if not tree:
            return None
        attr = next(iter(tree))
        branches = tree[attr]
        val = example.get(attr)
        if val not in branches:
            return None
        tree = branches[val]
    return tree

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

        #encontrar a posição vazia mais baixa na coluna:
        for row in range(5, -1, -1):
            if new_state.board[row][col] == '_':
                new_state.board[row][col] = self.current_player
                new_state.last_move = (row, col)
                new_state.current_player = 'O' if self.current_player == 'X' else 'X'
                return new_state
        return None

    def is_terminal(self):
        return self.get_winner() is not None or len(self.get_legal_moves()) == 0

    #verificação de vitória usando array de vetores de direção:
    def get_winner(self):
        directions = [
            (0, 1),  #horizontal
            (1, 0),  #vertical
            (1, 1),  #diagonal baixo-direita
            (1, -1)] #diagonal baixo-esquerda
        for row in range(6):
            for col in range(7):
                if self.board[row][col] == '_':
                    continue
                    
                for dr, dc in directions:
                    try:
                        if (self.board[row][col] == self.board[row + dr][col + dc] ==
                            self.board[row + 2*dr][col + 2*dc] == 
                            self.board[row + 3*dr][col + 3*dc] != '_'):
                            return 1 if self.board[row][col] == 'X' else -1
                    except IndexError: #Pula as verificações fora dos limites do tabuleiro
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
        #usando função lambda para determinar o filho com maior pontuação de ucb1 corretamente
        return max(self.children, key=lambda child: (child.total_value / child.visits if child.visits > 0 else float('inf')) + exploration_constant * math.sqrt(math.log(self.visits) / (child.visits if child.visits > 0 else 1)))

    def add_child(self, child_state):
        child = Node(child_state, self)
        self.children.append(child)
        return child
    
class ID3DecisionTree:
    def __init__(self):
        self.tree = {}
        self.features = ['state']

    def train(self, dataset):
        def build_tree(subset, used_features):
            counts = defaultdict(int)
            for row in subset:
                counts[row['move']] += 1
            
            if len(counts) == 1:
                return next(iter(counts.keys()))
            
            if len(used_features) >= len(self.features):
                return max(counts, key=counts.get)
            
            best_feature = self.choose_best_feature(subset, used_features)
            tree = {best_feature: {}}
            
            # Agrupa por valores únicos do estado completo
            for value in set(row[best_feature] for row in subset):
                subset_val = [row for row in subset if row[best_feature] == value]
                subtree = build_tree(subset_val, used_features + [best_feature])
                tree[best_feature][value] = subtree
            
            return tree

        self.tree = build_tree(dataset, [])

    def choose_best_feature(self, subset, used_features):
        # Implementação simplificada usando apenas a feature 'state'
        counts = defaultdict(int)
        for row in subset:
            counts[(row['state'], row['move'])] += 1
        
        # Prioriza estados que levam sempre ao mesmo movimento
        best_state = max(counts, key=lambda x: counts[x])
        return 'state'

    def predict(self, state):
        current_state = ''.join([''.join(row) for row in state.board])
        legal_moves = state.get_legal_moves()
        
        # Busca na árvore por estados completos conhecidos
        move = self.tree.get('state', {}).get(current_state, random.choice(legal_moves))
        return int(move) if str(move).isdigit() else random.choice(legal_moves)

def uct_search(state, num_iterations):
    root_node = Node(state)
    for _ in range(num_iterations):
        node = root_node
        current_state = state.clone()
        
        # Selection
        while not current_state.is_terminal() and node.is_fully_expanded():
            node = node.select_child()
            current_state = current_state.do_move(node.state.last_move[1])
        
        # Expansion
        if not current_state.is_terminal():
            unexplored_moves = [move for move in current_state.get_legal_moves() 
                              if move not in [child.state.last_move[1] 
                                            for child in node.children]]
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
        while node is not None:           #atribui +1 para vitória, 0 para empate, -1 para derrota
            node.visits += 1              #(do ponto de vista do jogador que fez o movimento)
            if result is not None:
                node_value = 1 if (result == 1 and node.state.current_player == 'O') or \
                                 (result == -1 and node.state.current_player == 'X') else -1
            else:
                node_value = 0
            node.total_value += node_value
            node = node.parent
    
    if root_node.children:
        return max(root_node.children, key=lambda c: c.visits).state.last_move[1]   #retorna o movimento mais visitado (mais consistente que maior valor)
    else:
        return random.choice(state.get_legal_moves())

def show_menu():
    print("\n" + "="*38)
    print("     CONNECT FOUR - Modos de Jogo")
    #print("     by Adelino, Martim e Rodrigo")
    print("="*38)
    print("1. Humano vs Humano (\U0001F464 x \U0001F464)")
    print("2. Humano vs Computador (\U0001F464 x \U0001F916)")
    print("3. Computador vs Computador (\U0001F916 x \U0001F916)")
    print("4. Sair")
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

id3_tree = ID3DecisionTree()

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

def main():
    iniciar_id3()
    while True:
        show_menu()
        try:
            choice = int(input("ESCOLHER MODO DE JOGO (1-4): "))
            if 1 <= choice <= 4:
                state = ConnectFourState()
                if choice == 1:
                    human_vs_human(state)
                elif choice == 2:
                    human_vs_pc(state)
                elif choice == 3:
                    pc_vs_pc(state)
                elif choice == 4:
                    print("Saindo do jogo. Até logo!")
                    break
            else:
                os.system('clear' if os.name == 'posix' else 'cls')
                print("\nOpção inválida. Tente novamente.\n")
        except ValueError:
            print("\nPor favor insira um número entre 1 e 4:\n")

if __name__ == "__main__":
    main()