def stringify_board(board):
    """Returns a nice string representation of a Connect Four board."""

    def checker(board_value):
        if board_value == 0:
            return "⚪"
        elif board_value == 1:
            return "🔴"
        elif board_value == 2:
            return "🟡"
        else:
            raise Exception(f"Invalid connect-four board value: {board_value}")

    mapped = [checker(val) for val in board]
    structured = ["".join(mapped[i : i + 7]) for i in range(0, 42, 7)]
    return "\n".join(structured)


def print_board(board):
    """Prints a nice string representation of a Connect Four board."""
    print(stringify_board(board))


def check_win_conditions(board):
    ''' Return 0 if no one has won
    Return 1 if red has won
    Return 2 if yellow has won 
    '''
    # convert board list to matrix to make easier to work with 
    # board_2d = [[board[i] for i in range(row*7,row*7+7)] for row in range(6)]

    for i in range(len(board)):
        curr_player = board[i]

        if curr_player != 0:
            if i % 7 in (0,1,2,3):
                # scan right horizontal (covers all possible combos dont need to check left)
                if all(board[j] == curr_player for j in range(i,i+4)):
                    return curr_player
            if i // 7 > 2:
                # scan bottom four pieces
                if all(board[j] == curr_player for j in range(i,i-22,-7)):
                    return curr_player
            if i in (0,1,2,3,7,8,9,10,14,15,16,17):
                # scan right diagonal
                if all(board[j] == curr_player for j in range(i,i+25,8)):
                    return curr_player
            
            if i in (3,4,5,6,10,11,12,13,17,18,19,20):
                # scan left diagonal
                if all(board[j] == curr_player for j in range(i,i+19,6)):
                    return curr_player
    return 0


def play_move(board, player, column):
    ''' Takes three inputs
    Board: list len 42 should be modified in place
    0 if empty location, 1 red, 2 yellow
    Player: integer person who is making move, 1 for red, 2 for yellow
    Column: integer between 0 and 6
    Raises exception if illegal move is attempted (checker dropped into full column)
    '''
    # checks all locations in column starting fromn lowest pos
    for i in range(35+column,column-1,-7):
        if board[i] == 0:
            board[i] = player 
            return

    raise ValueError("Column is full!")


if __name__ == "__main__":
    test_board = [0 for i in range(42)]

    # tests
    def check_horizontals():
        test_board = [0 for i in range(42)]
        play_move(test_board,1,2)
        play_move(test_board,1,3)
        play_move(test_board,1,4)
        play_move(test_board,1,5)
        print(check_win_conditions(test_board))
        print_board(test_board)

    def check_verticals():
        test_board = [0 for i in range(42)]
        play_move(test_board,1,1)
        play_move(test_board,2,1)
        play_move(test_board,1,1)
        play_move(test_board,1,1)
        play_move(test_board,1,1)
        play_move(test_board,1,1)
        print(check_win_conditions(test_board))
        print_board(test_board)

    def check_diagonals():
        test_board = [0 for i in range(42)]
        play_move(test_board,2,0)
        play_move(test_board,1,1)
        play_move(test_board,2,1)
        play_move(test_board,1,2)
        play_move(test_board,1,2)
        play_move(test_board,2,2)
        play_move(test_board,1,3)
        play_move(test_board,1,3)
        play_move(test_board,1,3)
        play_move(test_board,2,3)
        print(check_win_conditions(test_board))
        print_board(test_board)

    check_horizontals()
    check_verticals()
    check_diagonals()

