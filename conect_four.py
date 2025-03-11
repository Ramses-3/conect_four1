import os
# esta é a interface do jogo
# o jogo é jogado por dois jogadores,  x e 0 que alternam entre turnos

def create_board():
    board = []
    for row in range(6):
        board.append(["_"]*7)
    board.append([])
    return board

def show_board(board, turn):
    os.system('cls')  # os.system('clear') for linux
    print("Connect Four Game")
    print(f"It is currently {turn}'s turn")
    print("Make a move by choosing your coordinates to play")
    for row in board[:-1]:
        print(' ' + ' '.join(row))
    print(" " + "".join(board[-1]))
    print()

def check_stuck(board, move):
    return board[0][move] != "_"

def get_move(board):
    while True:
        try:
            move = int(input("Enter 0-6 to drop your piece in a column: ").strip())
            if 0 <= move <= 6 and not check_stuck(board, move):
                return move
            else:
                print("Try again. Choose a column 0-6:")
        except ValueError:
            print("Try again. That's not a number")

def make_move(board, move, turn):
    for i in range(5, -1, -1):  # Check from bottom up
        if board[i][move] == "_":
            board[i][move] = turn
            return board
    return board

def check_draw(board):
    for move in range(7):
        if not check_stuck(board, move):
            return False
    return True

def check_win(board, turn):
    # check horizontals
    for row in range(6):
        for col in range(4):
            if all(board[row][col+i] == turn for i in range(4)):
                return True
    
    # check verticals
    for row in range(3):
        for col in range(7):
            if all(board[row+i][col] == turn for i in range(4)):
                return True
    
    # check diagonals
    for row in range(3):
        for col in range(4):
            # down-right diagonal
            if all(board[row+i][col+i] == turn for i in range(4)):
                return True
            # down-left diagonal
            if all(board[row+i][col+3-i] == turn for i in range(4)):
                return True
    return False

def game():
    board = create_board()
    turn = "X"
    
    while True:
        show_board(board, turn)
        move = get_move(board)
        board = make_move(board, move, turn)
        
        if check_win(board, turn):
            show_board(board, turn)
            print(f"Player {turn} wins! Game over.")
            break
        elif check_draw(board):
            show_board(board, turn)
            print("Board full! Game over.")
            break
        
        turn = "O" if turn == "X" else "X"

if __name__ == "__main__":
    game()




