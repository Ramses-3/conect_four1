# connect_four_ai.py
import random
import math
import tkinter as tk #para o caso de implementação da interface grafica
import csv
import os
import json

# CONNECT FOUR
class ConnectFourState:
    def __init__(self):
        self.board = [['_'] * 7 for _ in range(6)]
        self.current_player = 'X'
        self.last_move = None

    def clone(self):
        new_state = ConnectFourState()
        new_state.board = [row[:] for row in self.board]
        new_state.current_player = self.current_player
        new_state.last_move = self.last_move
        return new_state

    def get_legal_moves(self):
        return [col for col in range(7) if self.board[0][col] == '_']

    def is_column_full(self, col):
        return self.board[0][col] != '_'

    def do_move(self, col):
        if self.is_column_full(col):
            return None
        new_state = self.clone()
        for row in range(5, -1, -1):
            if new_state.board[row][col] == '_':
                new_state.board[row][col] = self.current_player
                new_state.last_move = (row, col)
                new_state.current_player = 'O' if self.current_player == 'X' else 'X'
                return new_state
        return None

    def is_terminal(self):
        return self.get_winner() is not None or not self.get_legal_moves()

    def get_winner(self):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for row in range(6):
            for col in range(7):
                if self.board[row][col] == '_':
                    continue
                for dr, dc in directions:
                    try:
                        if (self.board[row][col] ==
                            self.board[row + dr][col + dc] ==
                            self.board[row + 2*dr][col + 2*dc] ==
                            self.board[row + 3*dr][col + 3*dc]):
                            return 1 if self.board[row][col] == 'X' else -1
                    except IndexError:
                        continue
        return None

# MCTS 
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
        return max(self.children, key=lambda child: (
            child.total_value / child.visits if child.visits > 0 else float('inf')
        ) + exploration_constant * math.sqrt(math.log(self.visits) / (child.visits if child.visits > 0 else 1)))

    def add_child(self, child_state):
        child = Node(child_state, self)
        self.children.append(child)
        return child

def uct_search(state, num_iterations):
    root_node = Node(state)
    for _ in range(num_iterations):
        node = root_node
        current_state = state.clone()

        while not current_state.is_terminal() and node.is_fully_expanded():
            node = node.select_child()
            current_state = current_state.do_move(node.state.last_move[1])

        if not current_state.is_terminal():
            unexplored_moves = [m for m in current_state.get_legal_moves()
                                if m not in [child.state.last_move[1] for child in node.children]]
            if unexplored_moves:
                move = random.choice(unexplored_moves)
                current_state = current_state.do_move(move)
                node = node.add_child(current_state)

        sim_state = current_state.clone()
        while not sim_state.is_terminal():
            sim_state = sim_state.do_move(random.choice(sim_state.get_legal_moves()))

        result = sim_state.get_winner()
        while node:
            node.visits += 1
            if result is not None:
                node_value = 1 if (result == 1 and node.state.current_player == 'O') or                                      (result == -1 and node.state.current_player == 'X') else -1
            else:
                node_value = 0
            node.total_value += node_value
            node = node.parent

    return max(root_node.children, key=lambda c: c.visits).state.last_move[1]

#  ÁRVORE DE DECISÃO SIMPLES 

# Default empty decision tree in case file is not found
id3_test_tree = {}

# Try to load the decision tree from file
try:
    with open("id3_tree_mcts.json") as f:
        id3_test_tree = json.load(f)
except FileNotFoundError:
    print("Warning: Decision tree file not found. Using random moves for ID3.")




def extract_abstract_features(board):
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

def id3_procedure(state):
    flat = [cell for row in state.board for cell in row]
    board = [flat[i*7:(i+1)*7] for i in range(6)]
    features = {f'cell_{i}': flat[i] for i in range(42)}
    features.update(extract_abstract_features(board))
    legal_moves = state.get_legal_moves()
    move = predict_with_tree(id3_test_tree, features)
    return move if isinstance(move, int) and move in legal_moves else random.choice(legal_moves)

#  GUI 
def create_gui_board():
    root = tk.Tk()
    root.title("Connect Four")
    for row in range(6):
        for col in range(7):
            btn = tk.Button(root, text="_", width=4, height=2)
            btn.grid(row=row, column=col)
    root.mainloop()

# DATASET GENERATION 
def generate_dataset(filename, num_games=100):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [f'cell_{i}' for i in range(42)] + ['move']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(num_games):
            state = ConnectFourState()
            while not state.is_terminal():
                features = {f'cell_{i}': cell for i, cell in enumerate(
                    [cell for row in state.board for cell in row])}
                move = uct_search(state, 100)
                features['move'] = move
                writer.writerow(features)
                state = state.do_move(move)

# TESTE 
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
    print(results)

# INTERFACE 
def show_menu():
    print("=" * 35)
    print("CONNECT FOUR")
    print("=" * 35)
    print("1. Humano vs Humano")
    print("2. Humano vs Computador")
    print("3. Computador vs Computador")
    print("4. Sair")
    print("=" * 35)

def print_board(board):
    os.system('clear' if os.name == 'posix' else 'cls')  # Limpa o terminal
    print(" 0 1 2 3 4 5 6")
    for row in board:
        print("|" + "|".join(row) + "|")
    print()

def get_human_move(state):
    while True:
        try:
            col = int(input(f"Jogador {state.current_player}, escolha uma coluna (0-6): "))
            if col in state.get_legal_moves():
                return col
            else:
                print("Movimento inválido. Tente novamente.")
        except ValueError:
            print("Por favor, insira um número válido.")

#  MODOS DE JOGO 
def human_vs_human():
    state = ConnectFourState()
    while not state.is_terminal():
        print_board(state.board)
        move = get_human_move(state)
        state = state.do_move(move)
    print_board(state.board)
    winner = state.get_winner()
    if winner == 1:
        print("Jogador X venceu!")
    elif winner == -1:
        print("Jogador O venceu!")
    else:
        print("Empate!")

def human_vs_computer():
    state = ConnectFourState()
    while not state.is_terminal():
        print_board(state.board)
        if state.current_player == 'X':
            move = get_human_move(state)
        else:
            print("Computador está pensando...")
            move = id3_procedure(state)  # Computador usa ID3 para decidir
        state = state.do_move(move)
    print_board(state.board)
    winner = state.get_winner()
    if winner == 1:
        print("Jogador X venceu!")
    elif winner == -1:
        print("Computador venceu!")
    else:
        print("Empate!")

def computer_vs_computer():
    simulate_pc_vs_pc(n=1) #escala de amostras geradas,posso por 10 ,20 

# MENU PRINCIPAL 
def main():
    while True:
        show_menu()
        choice = input("Escolha o modo (1-4): ")
        if choice == "1":
            human_vs_human()
        elif choice == "2":
            human_vs_computer()
        elif choice == "3":
            computer_vs_computer()
        elif choice == "4":
            print("Saindo do jogo. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
