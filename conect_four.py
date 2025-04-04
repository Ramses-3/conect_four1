import os
import random
import math

# TODO: Precisamos de uma interface pré-game ou que se passe por argumentos ao executar o programa para selecionarmos o modo de jogo e qual tipo de pesquisa será usada pela IA, se for jogar.

#falta melhorar diversas coisas no codigo ,como testar diferentes parâmetros para o UCT(numeros de simulações filhos por nós), e melhorar a interface gráfica
#melhorar eficiência do código e torna-lo mais agil para o usuario
#integrar o jogo para o modo humano vs computador : o computador deve tomar decisões inteligentes e não aleatórias contra o jogador humano
#de seguida as melhorias devemos tratar do dataset para arvore de decisão (ID3) para o treino do modelo 
#usar mcts para gerar estados do jogo e as melhores jogadas ,salvar esses dados como um dataset(cs.. ou json),
#criar banco de dados para treinar a arvore de decisão(não usar sckit learn ,ta escrito no enunciado)
#criar função para testar novas jogadas usando a arvore,o computador deve tomar decisões baseadas na arvore de decisão
#cenarios do jogo,humano vs humano ,humano vs computador,computador vs computador (compare os metodos )
#vejam  o codigo por inteiro por favor e comentem o que acham que deve ser melhorado ou adicionado,o que esta errado
def create_board():
    board = []
    for _ in range(6):
        board.append(["_"]*7)
    return board

def print_board(board):
    os.system('clear' if os.name == 'posix' else 'cls') #Comentar linha antes de executar para ver o tableaux
    print(" 0 1 2 3 4 5 6")
    for row in board:
        print("|" + "|".join(row) + "|")
    print()

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

        # Find the lowest empty position in the column
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
            (1, 1),  # diagonal down-right
            (1, -1)   # diagonal down-left
        ]
        
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
                    except IndexError:
                        continue
        return None

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_moves())
    
    def select_child(self):
        depth = self.get_depth()
        exploration_constant = 1.0 / math.sqrt(depth + 2.0)
        return max(self.children, key=lambda c: c.value/c.visits + exploration_constant * math.sqrt(2*math.log(self.visits)/c.visits))
    # comparar os valores de value/ visits

    def add_child(self, child_state):
        child = Node(child_state, self)
        self.children.append(child)
        return child

def uct_search(state, num_iterations):
    root_node = Node(state)
    
    for _ in range(num_iterations):
        node = root_node
        state = state.clone()
        
        while not state.is_terminal() and node.is_fully_expanded():
            node = node.select_child()
            state = state.do_move(node.state.last_move[1])  # Use column number

        # Expansion    
        if not state.is_terminal():
            unexplored_moves = [move for move in state.get_legal_moves() 
                              if move not in [child.state.last_move[1] 
                                            for child in node.children]]
            if unexplored_moves:
                chosen_move = random.choice(unexplored_moves)
                state = state.do_move(chosen_move)
                node = node.add_child(state)
        
        # Simulation
        while not state.is_terminal():
            legal_moves = state.get_legal_moves()
            if legal_moves:
                move = random.choice(legal_moves)
                state = state.do_move(move)
            else:
                break
        
        # Backpropagation
        while node is not None:
            node.visits += 1
            node.value += state.get_winner() if state.get_winner() is not None else 0
            node = node.parent
            
    return max(root_node.children, key=lambda c: c.visits).state.last_move[1]

def main():
    state = ConnectFourState()  
    
    while not state.is_terminal():
        print_board(state.board)
        
        if state.current_player == 'X':
            print("X plays\n")
            move = uct_search(state, 1000)
        else:
            print(f"O plays\n")
            while True:
                try:
                    col = int(input("Player {state.current_player}, choose column (0-6): "))
                    if 0 <= col <= 6 and not state.is_column_full(col):
                        move = col
                        break
                    print("Invalid move. Column full or out of range.")
                except ValueError:
                    print("Please enter a number between 0 and 6.")
        
        state = state.do_move(move)
    
    print_board(state.board)
    winner = state.get_winner()
    if winner == 1:
        print("X wins!")
    elif winner == -1:
        print("O wins!")
    else:
        print("Draw!")

if __name__ == "__main__":
    main()
    #implementação ta em jogador vs computador ,falta implementar jogador vs jogador e computador vs computador
    #falta implementar a arvore de decisão e o dataset para treino do modelo
    #falta implementar a função para testar novas jogadas usando a arvore de decisão
    #as regras do jogo não estão implementadas como deveriam,pode ser visto no tableaux apresentado quando o codigo é executado